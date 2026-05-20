from db.bootstrap import execute_schema_file
from repositories.system_repository import get_db_health


def health_db():
    return get_db_health()


def init_db():
    return execute_schema_file()
