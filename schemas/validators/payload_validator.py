from core.exceptions.app_exceptions import ValidationError
from models import MODEL_REGISTRY


def allowed_columns(table_name: str) -> set[str]:
    table = MODEL_REGISTRY[table_name]
    return {column.name for column in table.columns}


def required_columns_for_insert(table_name: str) -> set[str]:
    table = MODEL_REGISTRY[table_name]
    required: set[str] = set()
    for column in table.columns:
        if column.nullable:
            continue
        if column.default is not None:
            continue
        required.add(column.name)
    return required


def validate_payload_columns(payload: dict, table_name: str, excluded: set[str] | None = None):
    excluded = excluded or set()
    allowed = allowed_columns(table_name) - excluded
    unknown = sorted(set(payload.keys()) - allowed)
    if unknown:
        raise ValidationError(f"Unknown fields for {table_name}: {', '.join(unknown)}")


def validate_required_insert_fields(
    payload: dict,
    table_name: str,
    excluded: set[str] | None = None,
):
    excluded = excluded or set()
    required = required_columns_for_insert(table_name) - excluded
    missing = sorted(name for name in required if payload.get(name) is None)
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")
