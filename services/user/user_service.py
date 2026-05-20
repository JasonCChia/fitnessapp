from repositories import user_repository


def create_user(payload: dict):
    return user_repository.create_user(payload)


def list_users():
    return user_repository.list_users()


def get_user(user_id: str):
    return user_repository.get_user(user_id)


def update_user(user_id: str, payload: dict):
    return user_repository.update_user(user_id, payload)


def upsert_user_preferences(user_id: str, payload: dict):
    return user_repository.upsert_user_preferences(user_id, payload)


def get_user_preferences(user_id: str):
    return user_repository.get_user_preferences(user_id)


def create_food_preference(user_id: str, payload: dict):
    return user_repository.create_food_preference(user_id, payload)


def list_food_preferences(user_id: str, include_deleted: bool):
    return user_repository.list_food_preferences(user_id, include_deleted)


def soft_delete_food_preference(user_id: str, preference_id: str):
    return user_repository.soft_delete_food_preference(user_id, preference_id)


def onboarding(user_payload: dict, preferences_payload: dict, food_preferences: list, fitness_snapshot: dict | None):
    return user_repository.create_onboarding(
        user_payload=user_payload,
        preferences_payload=preferences_payload,
        food_preferences=food_preferences,
        fitness_snapshot=fitness_snapshot,
    )
