from typing import Dict, Optional, Tuple
import sys
import platform

import numpy as np
import pandas as pd
from google.protobuf.message import DecodeError
from pydantic import BaseModel
import requests
from requests.adapters import Retry
from requests.models import Response
from requests.sessions import HTTPAdapter

from common_client_scheduler import ErrorResponse, headers
from terality._terality.utils.config import CredentialsProvider
from terality.version import __version__
from terality.exceptions import TeralityError

_PLATFORM_INFO = platform.platform()

STATUS_CODE = int  # pylint: disable=invalid-name


class _ProcessInfo(BaseModel):
    """Info about the Python process using Terality."""

    python_version_major: str = str(sys.version_info.major)
    python_version_minor: str = str(sys.version_info.minor)
    python_version_micro: str = str(sys.version_info.micro)
    numpy_version: str = np.__version__
    pandas_version: str = pd.__version__
    terality_version: Optional[str] = __version__
    platform: str = _PLATFORM_INFO

    def to_headers(self) -> Dict[str, str]:
        return {f"{headers.TERALITY_CLIENT_INFO_PREFIX}{k}": v for k, v in self.dict().items()}


class HttpTransport:
    """Responsible for serializing and sending requests to the Terality API, as well as deserializing the response.

    This class handles:
    * serialization and deserialization
    * raising exceptions on non-success API responses
    * retries at the HTTP level
    * reloading credentials on auth errors

    This class largely ignores the HTTP response code, and instead always tries to deserialize the response body.
    If this fails, it raises a generic exception.

    Args:
        base_url: URL of the Terality API (such as "https://api.terality2.com")
        verify_ssl_certificate (deprecated): whether to valide the TLS certificate chain on HTTPS connections
        request_timeout: tuple of (connect timeout, read timeout) for HTTP requests, in seconds
        auth_credentials: credentials to add to HTTP requests
    """

    def __init__(
        self,
        base_url: str,
        *,
        verify_ssl_certificate: bool = True,
        request_timeout: Tuple[int, int] = (3, 30),  # connect, read
        credentials_provider: CredentialsProvider,
    ):
        self._http_session = requests.Session()
        self._base_url = base_url
        self._verify_ssl_certificate = verify_ssl_certificate
        self._request_timeout = request_timeout
        # Strip trailing slash
        if self._base_url.endswith("/"):
            self._base_url = self._base_url[:-1]

        self._credential_providers = credentials_provider
        self._process_info = _ProcessInfo()
        self._mount_http_adapter()

    def _mount_http_adapter(self):
        # We are encountering errors with the AWS API Gateway returning 404 or 403 errors.
        # (ref: https://console.aws.amazon.com/support/home#/case/?displayId=8464649331&language=en)
        # This issue won't be solved by AWS. It seems to occur shortly after the API Gateway is instantied,
        # which is common during integration tests. As a workaround, retry on all of these status codes.
        # Retries on 401 and 403 are manually handled by refreshing credentials before retrying.
        status_forcelist = [404, 413, 429, 500, 502, 503, 504]
        args = {
            "total": 3,
            # We are encountering errors with the AWS API Gateway returning 404 or 403 errors
            # (ref: https://console.aws.amazon.com/support/home#/case/?displayId=8464649331&language=en)
            # While we wait for AWS support to solve this issue, also retry those calls:
            "status_forcelist": status_forcelist,
            # We do retry on POST methods (retry pandas computations), even if there are not idempotent.
            "allowed_methods": ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            "backoff_factor": 1,
            "redirect": 40,
            "raise_on_redirect": True,
            "respect_retry_after_header": True,
            "raise_on_status": False,
        }
        try:
            retry_strategy = Retry(**args)
        except TypeError:
            # Support for urllib <= 1.26 (we want to support Google Colab which requires requests 2.23)
            args["method_whitelist"] = args.pop("allowed_methods")
            retry_strategy = Retry(**args)

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._http_session.mount("https://", adapter)
        self._http_session.mount("http://", adapter)

    @staticmethod
    def _return_content_or_raise(response: Response) -> Tuple[bytes, STATUS_CODE]:
        """
        Raise TeralityError if response status code received is not 2xx.
        The code 202 will represent pending responses (PendingComputationResponse).
        """

        if response.status_code // 100 == 2:
            return response.content, response.status_code

        if response.status_code // 100 == 1 or response.status_code // 100 == 3:
            raise TeralityError(
                f"Received an unexpected status code: {response.status_code}, expected 2xx, 4xx or 5xx."
            )

        try:
            error = ErrorResponse.parse(response.content)
            # The server representation does not include the request ID though, so we add it here.
            additional_info = HttpTransport._basic_info_from_response(response)
            raise TeralityError(f"{error.message} {additional_info}")
        except DecodeError as e:
            raise TeralityError(
                "Encountered an error while decoding the error response from server"
            ) from e

    def request(
        self,
        route: str,
        payload_b64: Optional[str] = None,
        method: str = "POST",
        session_id: Optional[str] = None,
    ) -> Tuple[bytes, STATUS_CODE]:
        """Perform an API request.

        Args:
            route: URL path (such as "/compute")
            payload_b64: object to send in the request body. Serialized with protobuf and encoded as str in base64.
            method: HTTP method (POST, GET, ...)
            session_id: if provided, add this session ID to the request.

        Return:
            the deserialized server response, and status code

        Raise:
            TeralityError: the server response could not be deserialized correcly
            Exception: when the server response body contains a serialized exception, it is propagated
        """
        self._set_auth_credentials(refresh=False)

        # Normalize route
        if not route.startswith("/"):
            route = "/" + route

        attempts = 0
        r = None
        while attempts <= 1:
            attempts += 1
            request_headers = self._make_request_headers(session_id)
            r = self._http_session.request(
                method=method,
                url=self._base_url + route,
                verify=self._verify_ssl_certificate,
                timeout=self._request_timeout,
                headers=request_headers,
                json={
                    "session_id": session_id,
                    "payload": payload_b64,
                },
            )
            if r.status_code in [401, 403]:
                self._set_auth_credentials(refresh=True)
            else:
                break

        assert r is not None
        return self._return_content_or_raise(r)

    def _set_auth_credentials(self, refresh: bool) -> None:
        auth_credentials = self._credential_providers.get_credentials(refresh)
        if auth_credentials is None:
            self._http_session.auth = None
            return
        self._http_session.auth = (auth_credentials.user, auth_credentials.password)

    def _make_request_headers(
        self,
        session_id: Optional[str],
    ) -> Dict[str, str]:
        request_headers = self._process_info.to_headers()
        if session_id:
            request_headers[headers.TERALITY_SESSION_ID] = session_id
        return request_headers

    @staticmethod
    def _extract_request_id(r: Response) -> Optional[str]:
        # The request may have failed before reaching a Terality application.
        # In that case, try to look for a request ID in headers added by AWS
        # infrastructure.
        headers_to_search = [headers.TERALITY_REQUEST_ID, "X-Amz-Apigw-Id", "Apigw-Requestid"]
        request_id = None

        for header in headers_to_search:
            request_id = r.headers.get(header)
            if request_id is not None:
                break

        return request_id

    @staticmethod
    def _basic_info_from_response(r: Response) -> str:
        request_id = HttpTransport._extract_request_id(r)
        if request_id is not None:
            info = f"(HTTP status {r.status_code}, request ID: {request_id})"
        else:
            info = f"(HTTP status {r.status_code})"
        return info
