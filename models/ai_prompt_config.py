from models.base import ColumnDefinition, TableDefinition


AI_PROMPT_CONFIGS_TABLE = TableDefinition(
    name="ai_prompt_configs",
    description="Prompt configuration per user and method with global fallback.",
    columns=(
        ColumnDefinition("config_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)", nullable=True),
        ColumnDefinition("method_name", "VARCHAR(100)"),
        ColumnDefinition("system_prompt", "TEXT"),
        ColumnDefinition("user_template", "TEXT"),
        ColumnDefinition("output_schema", "JSON", nullable=True),
        ColumnDefinition("temperature", "DECIMAL(3,2)", default="0.70"),
        ColumnDefinition("max_tokens", "SMALLINT", default="2000"),
        ColumnDefinition("is_default", "BOOLEAN", default="FALSE"),
        ColumnDefinition(
            "updated_at",
            "TIMESTAMP",
            default="CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        ),
    ),
    primary_key=("config_id",),
    indexes=(("user_id", "method_name"),),
)
