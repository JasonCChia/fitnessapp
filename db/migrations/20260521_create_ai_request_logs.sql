CREATE TABLE IF NOT EXISTS ai_request_logs (
  log_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  provider VARCHAR(50) NOT NULL COMMENT 'groq/etc',
  model_name VARCHAR(100) NULL COMMENT 'e.g. claude-3-5-sonnet, gpt-4o-mini',
  method_name VARCHAR(100) NOT NULL COMMENT 'Business method, e.g. generateMealPlan',
  request_payload JSON NULL,
  response_payload JSON NULL,
  input_tokens INT UNSIGNED NOT NULL DEFAULT 0,
  output_tokens INT UNSIGNED NOT NULL DEFAULT 0,
  total_tokens INT UNSIGNED NOT NULL DEFAULT 0,
  status ENUM('success','error') NOT NULL DEFAULT 'success',
  error_message TEXT NULL,
  requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_airl_user_requested (user_id, requested_at),
  KEY idx_airl_provider_method (provider, method_name),
  CONSTRAINT fk_airl_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
