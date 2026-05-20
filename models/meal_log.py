from models.base import ColumnDefinition, TableDefinition


MEAL_LOGS_TABLE = TableDefinition(
    name="meal_logs",
    description="Per-meal logs for calorie and macro tracking.",
    columns=(
        ColumnDefinition("log_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("log_date", "DATE"),
        ColumnDefinition("meal_type", "ENUM('breakfast','lunch','dinner','snack')"),
        ColumnDefinition("food_name", "VARCHAR(200)"),
        ColumnDefinition("portion_desc", "VARCHAR(100)", nullable=True),
        ColumnDefinition("calories", "SMALLINT"),
        ColumnDefinition("protein_g", "DECIMAL(5,1)", default="0.0"),
        ColumnDefinition("carbs_g", "DECIMAL(5,1)", default="0.0"),
        ColumnDefinition("fat_g", "DECIMAL(5,1)", default="0.0"),
        ColumnDefinition("ai_estimated", "BOOLEAN", default="FALSE"),
        ColumnDefinition("is_manual_input", "BOOLEAN", default="FALSE"),
        ColumnDefinition("allergy_flag", "BOOLEAN", default="FALSE"),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ),
    primary_key=("log_id",),
    indexes=(("user_id", "log_date"),),
)
