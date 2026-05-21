ALTER TABLE users
ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'Store hash only (werkzeug generate_password_hash)'
AFTER email;
