from dataclasses import asdict

from algoralabs.common.enum import PermissionRequest
from algoralabs.common.requests import __get_request, __put_request
from algoralabs.decorators.data import data_request


@data_request(transformer=lambda data: data)
def get_research(id: str):
    endpoint = f"research-service/research/{id}"
    return __get_request(endpoint)


@data_request(
    transformer=lambda data: data,
    process_response=lambda response: response.content
)
def get_resource(id: str):
    endpoint = f"research-service/resource/{id}/code"
    return __get_request(endpoint)


@data_request(transformer=lambda data: data)
def create_permission(request: PermissionRequest):
    endpoint = f"research-service/permission"
    return __put_request(endpoint, json=asdict(request))
