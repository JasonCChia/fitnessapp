from models.base import ColumnDefinition, TableDefinition


WEIGHT_LOGS_TABLE = TableDefinition(
    name="weight_logs",
    description="Daily or weekly body weight logs.",
    columns=(
        ColumnDefinition("log_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("log_date", "DATE"),
        ColumnDefinition("weight_kg", "DECIMAL(5,2)"),
        ColumnDefinition("notes", "TEXT", nullable=True),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ),
    primary_key=("log_id",),
    indexes=(("user_id", "log_date"),),
)
