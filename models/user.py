from models.base import ColumnDefinition, TableDefinition


USER_TABLE = TableDefinition(
    name="users",
    description="Master data user profile.",
    columns=(
        ColumnDefinition("user_id", "CHAR(36)", default="UUID()"),
        ColumnDefinition("name", "VARCHAR(100)"),
        ColumnDefinition("email", "VARCHAR(255)", nullable=True),
        ColumnDefinition("gender", "ENUM('male','female','other')"),
        ColumnDefinition("birth_date", "DATE"),
        ColumnDefinition("height_cm", "DECIMAL(4,1)"),
        ColumnDefinition("ai_provider", "VARCHAR(50)", default="'anthropic'"),
        ColumnDefinition("api_key_ref", "TEXT", nullable=True),
        ColumnDefinition("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ColumnDefinition("onboarding_done", "BOOLEAN", default="FALSE"),
    ),
    primary_key=("user_id",),
    unique_keys=(("email",),),
)
