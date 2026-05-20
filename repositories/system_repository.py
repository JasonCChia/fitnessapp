from repositories.common_repository import fetch_one


def get_db_health():
    return fetch_one("SELECT DATABASE() AS active_db, NOW() AS server_time")
