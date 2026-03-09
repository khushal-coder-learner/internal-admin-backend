import enum

class JobType(str, enum.Enum):
    export = "export"
    send_email = "send_email"
    bulk_user_email_dispatch = "bulk_user_email_dispatch"