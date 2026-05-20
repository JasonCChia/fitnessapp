from models.base import ColumnDefinition, TableDefinition


DAY_SCORES_TABLE = TableDefinition(
    name="day_scores",
    description="Daily discipline score snapshots; unique per user and date.",
    columns=(
        ColumnDefinition("score_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("score_date", "DATE"),
        ColumnDefinition("total_score", "TINYINT"),
        ColumnDefinition("workout_pts", "TINYINT", default="0"),
        ColumnDefinition("nutrition_pts", "TINYINT", default="0"),
        ColumnDefinition("sleep_pts", "TINYINT", default="0"),
        ColumnDefinition("logging_pts", "TINYINT", default="0"),
        ColumnDefinition("bonus_pts", "TINYINT", default="0"),
        ColumnDefinition("penalty_pts", "TINYINT", default="0"),
        ColumnDefinition("workout_done", "BOOLEAN", default="FALSE"),
        ColumnDefinition("is_rest_day", "BOOLEAN", default="FALSE"),
        ColumnDefinition("calories_actual", "SMALLINT", default="0"),
        ColumnDefinition("calories_target", "SMALLINT", default="0"),
        ColumnDefinition("sleep_hours_actual", "DECIMAL(3,1)", default="0.0"),
        ColumnDefinition("sleep_hours_target", "DECIMAL(3,1)", default="0.0"),
        ColumnDefinition("calculated_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ),
    primary_key=("score_id",),
    unique_keys=(("user_id", "score_date"),),
)
