import json

from repositories import prompt_repository


def list_ai_prompt_configs(user_id: str, method_name: str | None):
    return prompt_repository.list_ai_prompt_configs(user_id, method_name)


def upsert_ai_prompt_config(user_id: str, method_name: str, payload: dict):
    data = dict(payload)
    if data.get("output_schema") is not None:
        data["output_schema"] = json.dumps(data["output_schema"])
    return prompt_repository.upsert_ai_prompt_config(user_id, method_name, data)
