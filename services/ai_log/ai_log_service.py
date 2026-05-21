import json

from repositories import ai_request_log_repository


def create_ai_request_log(user_id: str, payload: dict):
    data = dict(payload)
    input_tokens = int(data.get("input_tokens") or 0)
    output_tokens = int(data.get("output_tokens") or 0)

    data["input_tokens"] = max(input_tokens, 0)
    data["output_tokens"] = max(output_tokens, 0)
    data["total_tokens"] = data["input_tokens"] + data["output_tokens"]

    if data.get("request_payload") is not None:
        data["request_payload"] = json.dumps(data["request_payload"])
    if data.get("response_payload") is not None:
        data["response_payload"] = json.dumps(data["response_payload"])

    return ai_request_log_repository.create_ai_request_log(user_id, data)


def list_ai_request_logs(
    user_id: str,
    provider: str | None,
    method_name: str | None,
    status: str | None,
    limit: int | None,
):
    safe_limit = max(1, min(int(limit or 50), 200))
    return ai_request_log_repository.list_ai_request_logs(
        user_id=user_id,
        provider=provider,
        method_name=method_name,
        status=status,
        limit=safe_limit,
    )
