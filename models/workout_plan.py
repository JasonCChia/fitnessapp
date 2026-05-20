from models.base import ColumnDefinition, TableDefinition


WORKOUT_PLANS_TABLE = TableDefinition(
    name="workout_plans",
    description="Workout plans with lifecycle states draft/active/archived.",
    columns=(
        ColumnDefinition("plan_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition("fitness_level_at", "TINYINT"),
        ColumnDefinition("status", "ENUM('active','archived','draft')", default="'draft'"),
        ColumnDefinition("goal_type", "ENUM('cut','bulk','maintain')"),
        ColumnDefinition("target_weight_kg", "DECIMAL(5,2)"),
        ColumnDefinition("weeks_data", "JSON"),
        ColumnDefinition("ai_generated", "BOOLEAN", default="FALSE"),
        ColumnDefinition("confirmed_at", "TIMESTAMP", nullable=True),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ColumnDefinition("archived_at", "TIMESTAMP", nullable=True),
    ),
    primary_key=("plan_id",),
    indexes=(("user_id", "status"),),
)
