from enum import Enum

class Permission(str, Enum):
    # Users
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DEACTIVATE = "user:deactivate"

    # Records
    RECORD_CREATE = "record:create"
    RECORD_VIEW = "record:view"
    RECORD_UPDATE = "record:update"
    RECORD_ASSIGN = "record:assign"
    RECORD_DELETE = "record:delete"

    # Activity Logs
    ACTIVITY_VIEW = "activity:view"


ROLE_PERMISSIONS = {
    "admin": {
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DEACTIVATE,
        Permission.RECORD_CREATE,
        Permission.RECORD_VIEW,
        Permission.RECORD_UPDATE,
        Permission.RECORD_ASSIGN,
        Permission.RECORD_DELETE,
        Permission.ACTIVITY_VIEW,
    },
    "staff": {
        Permission.RECORD_CREATE,
        Permission.RECORD_VIEW,
        Permission.RECORD_UPDATE,
    },
}
