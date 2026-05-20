from models.base import ColumnDefinition, TableDefinition


WORKOUT_SESSIONS_TABLE = TableDefinition(
    name="workout_sessions",
    description="Per-session workout logs linked to active plan when available.",
    columns=(
        ColumnDefinition("session_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("plan_id", "CHAR(36)", nullable=True),
        ColumnDefinition("session_date", "DATE"),
        ColumnDefinition("completed", "BOOLEAN", default="FALSE"),
        ColumnDefinition("completion_pct", "DECIMAL(4,1)", default="0.0"),
        ColumnDefinition("duration_min", "SMALLINT", nullable=True),
        ColumnDefinition("exercises_log", "JSON"),
        ColumnDefinition("user_notes", "TEXT", nullable=True),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ),
    primary_key=("session_id",),
    indexes=(("user_id", "session_date"),),
)
