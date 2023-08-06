from dataclasses import asdict

from algoralabs.common.enum import PermissionRequest
from algoralabs.common.requests import __delete_request, __put_request
from algoralabs.decorators.data import data_request


def delete_document(id: str):
    endpoint = f"document-registry/documents/{id}"
    return __delete_request(endpoint)


@data_request(transformer=lambda data: data)
def create_permission(request: PermissionRequest):
    endpoint = f"document-registry/documents/permission"
    return __put_request(endpoint, json=asdict(request))
