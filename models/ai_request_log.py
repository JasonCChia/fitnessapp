from models.base import ColumnDefinition, TableDefinition


AI_REQUEST_LOGS_TABLE = TableDefinition(
    name="ai_request_logs",
    description="Per-user audit log for AI requests and token usage.",
    columns=(
        ColumnDefinition("log_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("provider", "VARCHAR(50)"),
        ColumnDefinition("model_name", "VARCHAR(100)", nullable=True),
        ColumnDefinition("method_name", "VARCHAR(100)"),
        ColumnDefinition("request_payload", "JSON", nullable=True),
        ColumnDefinition("response_payload", "JSON", nullable=True),
        ColumnDefinition("input_tokens", "INT UNSIGNED", default="0"),
        ColumnDefinition("output_tokens", "INT UNSIGNED", default="0"),
        ColumnDefinition("total_tokens", "INT UNSIGNED", default="0"),
        ColumnDefinition("status", "ENUM('success','error')", default="'success'"),
        ColumnDefinition("error_message", "TEXT", nullable=True),
        ColumnDefinition("requested_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ),
    primary_key=("log_id",),
    indexes=(("user_id", "requested_at"), ("provider", "method_name")),
)
