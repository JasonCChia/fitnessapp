from db.connection import db_cursor


def new_uuid(cursor) -> str:
    cursor.execute("SELECT UUID() AS new_id")
    return cursor.fetchone()["new_id"]


def fetch_one(query: str, params: tuple | None = None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchone()


def fetch_all(query: str, params: tuple | None = None):
    with db_cursor() as (_, cursor):
        cursor.execute(query, params or ())
        return cursor.fetchall()
