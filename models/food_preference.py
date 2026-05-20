from models.base import ColumnDefinition, TableDefinition


FOOD_PREFERENCES_TABLE = TableDefinition(
    name="food_preferences",
    description="Food preferences and restrictions with soft-delete.",
    columns=(
        ColumnDefinition("preference_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("user_id", "CHAR(36)"),
        ColumnDefinition(
            "category", "ENUM('liked','disliked','allergy','intolerance','religious')"
        ),
        ColumnDefinition("food_name", "VARCHAR(100)", nullable=True),
        ColumnDefinition("food_group", "VARCHAR(100)", nullable=True),
        ColumnDefinition("severity", "ENUM('hard','soft')", default="'soft'"),
        ColumnDefinition("note", "TEXT", nullable=True),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ColumnDefinition("deleted_at", "TIMESTAMP", nullable=True),
    ),
    primary_key=("preference_id",),
    indexes=(("user_id", "deleted_at"),),
)
