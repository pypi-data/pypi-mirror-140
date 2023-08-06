from functools import partial
from typing import Optional, Any, Union

from terality_serde import apply_func_on_object_recursively, StructType, IndexType, dumps
from terality.exceptions import TeralityError
from terality._terality.globals import global_client
from terality._terality.encoding import encode, decode
from terality._terality.utils import logger


def call_pandas_function(  # pylint: disable=too-many-locals
    function_type: Union[StructType, IndexType],
    function_prefix: Optional[str],
    function_name: str,
    *args,
    **kwargs,
) -> Any:
    args = [] if args is None else args
    args_encoded = apply_func_on_object_recursively(
        args, partial(encode, global_client().get_aws_credentials(), function_name)
    )
    kwargs = {} if kwargs is None else kwargs
    kwargs_encoded = apply_func_on_object_recursively(
        kwargs, partial(encode, global_client().get_aws_credentials(), function_name)
    )

    response = global_client().compute_pandas(
        function_type=function_type,
        function_prefix=function_prefix,
        function_name=function_name,
        args_encoded=dumps(args_encoded),
        kwargs_encoded=dumps(kwargs_encoded),
    )

    result = response.result
    result = apply_func_on_object_recursively(
        result, partial(decode, global_client().get_aws_credentials())
    )

    # Handle in-place modification of data structures.
    # NOTE: Because `inplace` is only available on methods, the first argument is guaranteed to be positional
    # (`self`).
    if response.inplace:
        from terality._terality.terality_structures.structure import (
            Struct,
        )  # break cyclic import

        if not isinstance(args[0], Struct):
            raise TeralityError("Received in-place response but the target is not a data structure")
        target = args[0]
        if not isinstance(result, Struct):
            raise TeralityError("Received in-place response but the result is not a data structure")
        # noinspection PyProtectedMember
        target._mutate(result)
        result = None

    for message in response.messages:
        logger.log(message.log_level, message.message)

    return result
