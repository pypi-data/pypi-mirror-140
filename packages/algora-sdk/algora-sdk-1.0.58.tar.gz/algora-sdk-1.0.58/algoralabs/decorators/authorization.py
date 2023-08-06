import functools
import json
import logging
from typing import Tuple, Dict, Any, Callable, Optional

import requests
from cachetools import cached, TTLCache

from algoralabs.common.config import EnvironmentConfig
from algoralabs.common.errors import AuthenticationError

logger = logging.getLogger(__name__)


# TODO: Figure out max size
@cached(cache=TTLCache(maxsize=100, ttl=6000))
def authenticate(base_url: str, username: str, password: str) -> dict:
    # TODO: add url and username and password to config
    auth_response = requests.post(
        url=f"{base_url}/login",
        data=json.dumps({"username": username, "password": password}),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )

    if auth_response.status_code == 200:
        bearer_token = auth_response.json()['access_token']
        return {'Authorization': f'Bearer {bearer_token}'}
    else:
        error = AuthenticationError("Failed to authenticate the user")
        logger.error(error)
        raise error


def authenticated_request(
        request: Callable = None,
        *,
        env_config: Optional[EnvironmentConfig] = None
) -> Callable:
    """
    """

    @functools.wraps(request)
    def decorator(f):
        @functools.wraps(f)
        def wrap(*args: Tuple, **kwargs: Dict[str, Any]) -> Any:
            """
            Wrapper for the decorated function

            Args:
                *args: args for the function
                **kwargs: keyword args for the function

            Returns:
                The output of the wrapped function
            """
            config = env_config if env_config is not None else EnvironmentConfig()

            if config.auth_config.token:
                auth_headers = json.loads(config.auth_config.token)
            elif config.auth_config.username and config.auth_config.password:
                auth_headers = authenticate(
                    base_url=config.base_url,
                    username=config.auth_config.username,
                    password=config.auth_config.password
                )
            else:
                raise AuthenticationError("Authentication for the package was configured incorrectly and is either "
                                          "missing a TOKEN or ALGORA_USER and ALGORA_PWD environment variable(s)")

            headers = kwargs.get("headers", {})
            headers.update(auth_headers)
            kwargs["headers"] = headers

            return f(*args, **kwargs)

        return wrap

    if request is None:
        return decorator
    return decorator(request)
