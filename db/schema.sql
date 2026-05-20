CREATE TABLE IF NOT EXISTS users (
  user_id CHAR(36) NOT NULL DEFAULT (UUID()),
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NULL,
  gender ENUM('male','female','other') NOT NULL,
  birth_date DATE NOT NULL,
  height_cm DECIMAL(4,1) NOT NULL,
  ai_provider VARCHAR(50) NOT NULL DEFAULT 'anthropic',
  api_key_ref TEXT NULL COMMENT 'Keychain reference string only - never the key value itself',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  onboarding_done BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_preferences (
  pref_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  sleep_target_hours DECIMAL(3,1) NOT NULL DEFAULT 8.0,
  activity_level ENUM('sedentary','light','moderate','active') NOT NULL,
  goal_type ENUM('cut','bulk','maintain') NOT NULL,
  goal_weight_kg DECIMAL(5,2) NOT NULL,
  goal_deadline_date DATE NULL,
  last_monthly_review_at TIMESTAMP NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (pref_id),
  UNIQUE KEY uq_user_preferences_user (user_id),
  CONSTRAINT fk_prefs_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS weight_logs (
  log_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  log_date DATE NOT NULL,
  weight_kg DECIMAL(5,2) NOT NULL,
  notes TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_weight_logs_user_date (user_id, log_date),
  CONSTRAINT fk_wl_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fitness_capabilities (
  capability_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  source ENUM('onboarding','monthly_review','manual') NOT NULL,
  fitness_level TINYINT NOT NULL,
  body_weight_kg DECIMAL(5,2) NOT NULL,
  body_fat_pct DECIMAL(4,1) NULL,
  resting_hr_bpm SMALLINT NULL,
  vo2max_estimate DECIMAL(4,1) NULL,
  pushup_max_reps SMALLINT NULL,
  pullup_max_reps SMALLINT NULL,
  squat_1rm_kg DECIMAL(5,2) NULL,
  deadlift_1rm_kg DECIMAL(5,2) NULL,
  run_5k_minutes DECIMAL(5,1) NULL,
  weekly_active_days TINYINT NULL,
  avg_session_min SMALLINT NULL,
  monthly_task_done SMALLINT NULL,
  monthly_task_total SMALLINT NULL,
  completion_rate_pct DECIMAL(4,1) NULL,
  ai_notes TEXT NULL,
  PRIMARY KEY (capability_id),
  KEY idx_fc_user_recorded (user_id, recorded_at),
  CONSTRAINT chk_fc_level CHECK (fitness_level BETWEEN 1 AND 5),
  CONSTRAINT fk_fc_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS food_preferences (
  preference_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  category ENUM('liked','disliked','allergy','intolerance','religious') NOT NULL,
  food_name VARCHAR(100) NULL,
  food_group VARCHAR(100) NULL,
  severity ENUM('hard','soft') NOT NULL DEFAULT 'soft',
  note TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  PRIMARY KEY (preference_id),
  KEY idx_fp_user_active (user_id, deleted_at),
  CONSTRAINT fk_fp_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workout_plans (
  plan_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  fitness_level_at TINYINT NOT NULL,
  status ENUM('active','archived','draft') NOT NULL DEFAULT 'draft',
  goal_type ENUM('cut','bulk','maintain') NOT NULL,
  target_weight_kg DECIMAL(5,2) NOT NULL,
  weeks_data JSON NOT NULL COMMENT 'Structure: { weeks: [{ day, isRestDay, sessions: [...] }] }',
  ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
  confirmed_at TIMESTAMP NULL COMMENT 'Weekly review trigger uses this field',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  archived_at TIMESTAMP NULL,
  PRIMARY KEY (plan_id),
  KEY idx_wp_user_status (user_id, status),
  CONSTRAINT fk_wp_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workout_sessions (
  session_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  plan_id CHAR(36) NULL COMMENT 'NULL for free sessions outside active plan',
  session_date DATE NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE,
  completion_pct DECIMAL(4,1) NOT NULL DEFAULT 0.0,
  duration_min SMALLINT NULL,
  exercises_log JSON NOT NULL COMMENT 'Array: [{name, sets, reps, weight_kg, notes}]',
  user_notes TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (session_id),
  KEY idx_ws_user_date (user_id, session_date),
  CONSTRAINT fk_ws_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_ws_plan
    FOREIGN KEY (plan_id) REFERENCES workout_plans(plan_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS meal_plans (
  plan_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  status ENUM('active','archived','draft') NOT NULL DEFAULT 'draft',
  target_calories SMALLINT NOT NULL,
  target_protein_g SMALLINT NOT NULL,
  target_carbs_g SMALLINT NOT NULL,
  target_fat_g SMALLINT NOT NULL,
  days_data JSON NOT NULL COMMENT 'Structure: { days: [...] }',
  preference_snapshot JSON NULL COMMENT 'Snapshot food_preferences when plan was created',
  ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
  confirmed_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (plan_id),
  KEY idx_mp_user_status (user_id, status),
  CONSTRAINT fk_mp_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS meal_logs (
  log_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  log_date DATE NOT NULL,
  meal_type ENUM('breakfast','lunch','dinner','snack') NOT NULL,
  food_name VARCHAR(200) NOT NULL,
  portion_desc VARCHAR(100) NULL,
  calories SMALLINT NOT NULL,
  protein_g DECIMAL(5,1) NOT NULL DEFAULT 0.0,
  carbs_g DECIMAL(5,1) NOT NULL DEFAULT 0.0,
  fat_g DECIMAL(5,1) NOT NULL DEFAULT 0.0,
  ai_estimated BOOLEAN NOT NULL DEFAULT FALSE,
  is_manual_input BOOLEAN NOT NULL DEFAULT FALSE,
  allergy_flag BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_ml_user_date (user_id, log_date),
  CONSTRAINT fk_ml_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS day_scores (
  score_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  score_date DATE NOT NULL,
  total_score TINYINT NOT NULL,
  workout_pts TINYINT NOT NULL DEFAULT 0,
  nutrition_pts TINYINT NOT NULL DEFAULT 0,
  sleep_pts TINYINT NOT NULL DEFAULT 0,
  logging_pts TINYINT NOT NULL DEFAULT 0,
  bonus_pts TINYINT NOT NULL DEFAULT 0,
  penalty_pts TINYINT NOT NULL DEFAULT 0 COMMENT 'Negative value, e.g. -10',
  workout_done BOOLEAN NOT NULL DEFAULT FALSE,
  is_rest_day BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Derived from workout_plans.weeks_data',
  calories_actual SMALLINT NOT NULL DEFAULT 0,
  calories_target SMALLINT NOT NULL DEFAULT 0,
  sleep_hours_actual DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  sleep_hours_target DECIMAL(3,1) NOT NULL DEFAULT 0.0 COMMENT 'Snapshot from user_preferences.sleep_target_hours',
  calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (score_id),
  UNIQUE KEY uq_day_scores_user_date (user_id, score_date),
  CONSTRAINT fk_ds_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ai_prompt_configs (
  config_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NULL COMMENT 'NULL = global default config',
  method_name VARCHAR(100) NOT NULL,
  system_prompt TEXT NOT NULL,
  user_template TEXT NOT NULL,
  output_schema JSON NULL,
  temperature DECIMAL(3,2) NOT NULL DEFAULT 0.70,
  max_tokens SMALLINT NOT NULL DEFAULT 2000,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (config_id),
  KEY idx_apc_user_method (user_id, method_name),
  CONSTRAINT fk_apc_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
