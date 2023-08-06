from typing import Optional

import requests

from algoralabs.common.config import EnvironmentConfig
from algoralabs.decorators.authorization import authenticated_request


@authenticated_request
def __get_request(endpoint: str, headers: Optional[dict] = None, params: Optional[dict] = None):
    return requests.get(
        url=f"{EnvironmentConfig().base_url}/{endpoint}",
        headers=headers or {},
        params=params
    )


@authenticated_request
def __put_request(endpoint: str, data=None, json=None, headers: Optional[dict] = None, params: Optional[dict] = None):
    return requests.put(
        url=f"{EnvironmentConfig().base_url}/{endpoint}",
        data=data,
        json=json,
        headers=headers or {},
        params=params
    )


@authenticated_request
def __post_request(endpoint: str, data=None, json=None, headers: Optional[dict] = None, params: Optional[dict] = None):
    return requests.post(
        url=f"{EnvironmentConfig().base_url}/{endpoint}",
        data=data,
        json=json,
        headers=headers or {},
        params=params
    )


@authenticated_request
def __delete_request(endpoint: str, headers: Optional[dict] = None, params: Optional[dict] = None):
    return requests.delete(
        url=f"{EnvironmentConfig().base_url}/{endpoint}",
        headers=headers or {},
        params=params
    )
