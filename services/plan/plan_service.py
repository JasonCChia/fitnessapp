from repositories import plan_repository


def create_workout_plan(user_id: str, payload: dict):
    return plan_repository.create_workout_plan(user_id, payload)


def list_workout_plans(user_id: str, status: str | None):
    return plan_repository.list_workout_plans(user_id, status)


def activate_workout_plan(user_id: str, plan_id: str):
    return plan_repository.activate_workout_plan(user_id, plan_id)


def create_meal_plan(user_id: str, payload: dict):
    return plan_repository.create_meal_plan(user_id, payload)


def list_meal_plans(user_id: str, status: str | None):
    return plan_repository.list_meal_plans(user_id, status)


def activate_meal_plan(user_id: str, plan_id: str):
    return plan_repository.activate_meal_plan(user_id, plan_id)


def get_active_program(user_id: str):
    return plan_repository.get_active_program(user_id)
