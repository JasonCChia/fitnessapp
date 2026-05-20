from models.base import ColumnDefinition, TableDefinition


USER_PREFERENCES_TABLE = TableDefinition(
    name="user_preferences",
    description="One row per user for mutable preferences and goals.",
    columns=(
        ColumnDefinition("pref_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("sleep_target_hours", "DECIMAL(3,1)", default="8.0"),
        ColumnDefinition(
            "activity_level", "ENUM('sedentary','light','moderate','active')"
        ),
        ColumnDefinition("goal_type", "ENUM('cut','bulk','maintain')"),
        ColumnDefinition("goal_weight_kg", "DECIMAL(5,2)"),
        ColumnDefinition("goal_deadline_date", "DATE", nullable=True),
        ColumnDefinition("last_monthly_review_at", "TIMESTAMP", nullable=True),
        ColumnDefinition(
            "updated_at",
            "TIMESTAMP",
            default="CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        ),
    ),
    primary_key=("pref_id",),
    unique_keys=(("user_id",),),
)
