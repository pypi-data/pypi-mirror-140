from dataclasses import dataclass
from enum import Enum


@dataclass
class CoreEnum:
    name: str
    value: str


class PermissionType(Enum):
    USER_ID = CoreEnum("", "USER_ID")
    GROUP = CoreEnum("", "GROUP")
    ROLE = CoreEnum("", "ROLE")


@dataclass
class PermissionRequest:
    resource_id: str
    permission_type: str  # TODO
    permission_id: str
    view: bool
    edit: bool
    delete: bool
    edit_permission: bool


class FieldType(Enum):
    BOOLEAN = 'BOOLEAN'
    DOUBLE = 'DOUBLE'
    INTEGER = 'INTEGER'
    TEXT = 'TEXT'
    TIMESTAMP = 'TIMESTAMP'
    UNKNOWN = 'UNKNOWN'


@dataclass
class Field:
    logical_name: str
    type: FieldType

    def as_dict(self):
        return {
            'logical_name': self.logical_name,
            'type': self.type.value
        }
