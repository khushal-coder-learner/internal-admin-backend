from enum import Enum

class Permission(str, Enum):
    # Users
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_STATUS_CHANGE = "user:status"

    # Records
    RECORD_CREATE = "record:create"
    RECORD_VIEW = "record:view"
    RECORD_UPDATE = "record:update"
    RECORD_ASSIGN = "record:assign"
    RECORD_DELETE = "record:delete"

    # Activity Logs
    ACTIVITY_VIEW = "activity:view"

    # Jobs
    JOB_VIEW = "jobs:view"
    EXPORT_JOB = "jobs:export"
    SEND_ANNOUNCEMENT = "jobs:announcement"


ROLE_PERMISSIONS = {
    "admin": {
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_STATUS_CHANGE,
        Permission.RECORD_CREATE,
        Permission.RECORD_VIEW,
        Permission.RECORD_UPDATE,
        Permission.RECORD_ASSIGN,
        Permission.RECORD_DELETE,
        Permission.ACTIVITY_VIEW,
        Permission.EXPORT_JOB,
        Permission.SEND_ANNOUNCEMENT,
        Permission.JOB_VIEW
    },
    "staff": {
        Permission.RECORD_CREATE,
        Permission.RECORD_VIEW,
        Permission.RECORD_UPDATE,
    },
}
