from dataclasses import asdict

from algoralabs.common.enum import PermissionRequest
from algoralabs.common.requests import __delete_request, __put_request, __post_request
from algoralabs.decorators.data import data_request


def delete_field(id: str):
    endpoint = f"data/datasets/field/{id}"
    return __delete_request(endpoint)


def delete_schema(id: str):
    endpoint = f"data/datasets/schema/{id}"
    return __delete_request(endpoint)


def delete_dataset(id: str):
    endpoint = f"data/datasets/dataset/{id}"
    return __delete_request(endpoint)


def query_dataset(id: str, data=None, json=None):
    """
    Query dataset by ID

    Args:
        id: UUID of dataset
        data: (Optional) Data to POST
        json: (Optional) Data to POST

    Returns: HTTP Response Object
    """
    endpoint = f"data/datasets/query/{id}"
    return __post_request(endpoint, data=data, json=json)


@data_request(transformer=lambda data: data)
def create_permission(request: PermissionRequest):
    endpoint = f"data/datasets/permission"
    return __put_request(endpoint, json=asdict(request))
