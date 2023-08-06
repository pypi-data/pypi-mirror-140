from terality._terality.utils.config import TeralityConfig, TeralityCredentials, ConfigError


def has_valid_terality_config_file() -> bool:
    try:
        TeralityConfig.load()
        return True
    except ConfigError:
        return False


def has_valid_terality_credentials_file() -> bool:
    try:
        TeralityCredentials.load()
        return True
    except ConfigError:
        return False
