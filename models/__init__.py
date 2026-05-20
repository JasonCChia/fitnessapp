from models.ai_prompt_config import AI_PROMPT_CONFIGS_TABLE
from models.base import TableDefinition
from models.day_score import DAY_SCORES_TABLE
from models.fitness_capability import FITNESS_CAPABILITIES_TABLE
from models.food_preference import FOOD_PREFERENCES_TABLE
from models.meal_log import MEAL_LOGS_TABLE
from models.meal_plan import MEAL_PLANS_TABLE
from models.user import USER_TABLE
from models.user_preferences import USER_PREFERENCES_TABLE
from models.weight_log import WEIGHT_LOGS_TABLE
from models.workout_plan import WORKOUT_PLANS_TABLE
from models.workout_session import WORKOUT_SESSIONS_TABLE


ALL_TABLES: tuple[TableDefinition, ...] = (
    USER_TABLE,
    USER_PREFERENCES_TABLE,
    WEIGHT_LOGS_TABLE,
    FITNESS_CAPABILITIES_TABLE,
    FOOD_PREFERENCES_TABLE,
    WORKOUT_PLANS_TABLE,
    WORKOUT_SESSIONS_TABLE,
    MEAL_PLANS_TABLE,
    MEAL_LOGS_TABLE,
    DAY_SCORES_TABLE,
    AI_PROMPT_CONFIGS_TABLE,
)

MODEL_REGISTRY: dict[str, TableDefinition] = {table.name: table for table in ALL_TABLES}
