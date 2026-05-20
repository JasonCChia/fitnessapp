from models.base import ColumnDefinition, TableDefinition


FITNESS_CAPABILITIES_TABLE = TableDefinition(
    name="fitness_capabilities",
    description="Append-only monthly capability snapshots.",
    columns=(
        ColumnDefinition("capability_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("recorded_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ColumnDefinition("source", "ENUM('onboarding','monthly_review','manual')"),
        ColumnDefinition("fitness_level", "TINYINT"),
        ColumnDefinition("body_weight_kg", "DECIMAL(5,2)"),
        ColumnDefinition("body_fat_pct", "DECIMAL(4,1)", nullable=True),
        ColumnDefinition("resting_hr_bpm", "SMALLINT", nullable=True),
        ColumnDefinition("vo2max_estimate", "DECIMAL(4,1)", nullable=True),
        ColumnDefinition("pushup_max_reps", "SMALLINT", nullable=True),
        ColumnDefinition("pullup_max_reps", "SMALLINT", nullable=True),
        ColumnDefinition("squat_1rm_kg", "DECIMAL(5,2)", nullable=True),
        ColumnDefinition("deadlift_1rm_kg", "DECIMAL(5,2)", nullable=True),
        ColumnDefinition("run_5k_minutes", "DECIMAL(5,1)", nullable=True),
        ColumnDefinition("weekly_active_days", "TINYINT", nullable=True),
        ColumnDefinition("avg_session_min", "SMALLINT", nullable=True),
        ColumnDefinition("monthly_task_done", "SMALLINT", nullable=True),
        ColumnDefinition("monthly_task_total", "SMALLINT", nullable=True),
        ColumnDefinition("completion_rate_pct", "DECIMAL(4,1)", nullable=True),
        ColumnDefinition("ai_notes", "TEXT", nullable=True),
    ),
    primary_key=("capability_id",),
    indexes=(("user_id", "recorded_at"),),
)
