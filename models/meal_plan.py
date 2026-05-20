from models.base import ColumnDefinition, TableDefinition


MEAL_PLANS_TABLE = TableDefinition(
    name="meal_plans",
    description="Meal plans with macro targets and generated day menu data.",
    columns=(
        ColumnDefinition("plan_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("status", "ENUM('active','archived','draft')", default="'draft'"),
        ColumnDefinition("target_calories", "SMALLINT"),
        ColumnDefinition("target_protein_g", "SMALLINT"),
        ColumnDefinition("target_carbs_g", "SMALLINT"),
        ColumnDefinition("target_fat_g", "SMALLINT"),
        ColumnDefinition("days_data", "JSON"),
        ColumnDefinition("preference_snapshot", "JSON", nullable=True),
        ColumnDefinition("ai_generated", "BOOLEAN", default="FALSE"),
        ColumnDefinition("confirmed_at", "TIMESTAMP", nullable=True),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ),
    primary_key=("plan_id",),
    indexes=(("user_id", "status"),),
)
