import os
from typing import Optional

from algoralabs.decorators.configuration import configuration
from algoralabs.gData import config_file


@configuration
class Auth:
    # Feature to keep values hidden from printing (not totally)
    # Allows for dynamic rendering of auth values
    @property
    def username(self) -> Optional[str]:
        return os.getenv("ALGORA_USER", None)

    @property
    def password(self) -> Optional[str]:
        return os.getenv("ALGORA_PWD", None)

    @property
    def token(self) -> Optional[str]:
        return os.getenv("AUTH_TOKEN", None)


@configuration(yaml_file=config_file, prefix="")
class AppConfig:
    app_name: str
    environment: str
    version: str


app_config = AppConfig()


@configuration(yaml_file=config_file, prefix=app_config.environment)
class EnvironmentConfig:
    base_url: str
    auth_config: Auth = Auth()
