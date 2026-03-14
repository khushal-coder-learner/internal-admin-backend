from .records_export import generate_records_csv
from .users_export import generate_users_csv
from .activity_logs_export import generate_activity_logs_csv


EXPORT_GENERATORS = {
    "records": generate_records_csv,
    "users": generate_users_csv,
    "activity_logs": generate_activity_logs_csv,
}