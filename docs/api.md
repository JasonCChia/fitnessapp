# API Modules

## Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

## System
- `GET /api/system/health/db`
- `POST /api/system/init-db`

## Users
- `POST /api/users`
- `GET /api/users`
- `GET /api/users/<user_id>`
- `PATCH /api/users/<user_id>`
- `POST /api/users/onboarding`

## Preferences
- `PUT /api/users/<user_id>/preferences`
- `GET /api/users/<user_id>/preferences`
- `POST /api/users/<user_id>/food-preferences`
- `GET /api/users/<user_id>/food-preferences`
- `DELETE /api/users/<user_id>/food-preferences/<preference_id>`

## Plans
- `POST /api/users/<user_id>/workout-plans`
- `GET /api/users/<user_id>/workout-plans`
- `POST /api/users/<user_id>/workout-plans/<plan_id>/activate`
- `POST /api/users/<user_id>/meal-plans`
- `GET /api/users/<user_id>/meal-plans`
- `POST /api/users/<user_id>/meal-plans/<plan_id>/activate`
- `GET /api/users/<user_id>/active-program`

## Tracking
- `POST /api/users/<user_id>/weight-logs`
- `GET /api/users/<user_id>/weight-logs`
- `POST /api/users/<user_id>/workout-sessions`
- `GET /api/users/<user_id>/workout-sessions`
- `POST /api/users/<user_id>/meal-logs`
- `GET /api/users/<user_id>/meal-logs`
- `PUT /api/users/<user_id>/day-scores/<score_date>`
- `GET /api/users/<user_id>/day-scores`
- `POST /api/users/<user_id>/fitness-capabilities`
- `GET /api/users/<user_id>/fitness-capabilities`

## Reviews & Prompt Config
- `GET /api/users/<user_id>/reviews/weekly`
- `POST /api/users/<user_id>/reviews/monthly/check-trigger`
- `POST /api/users/<user_id>/reviews/monthly/mark-done`
- `GET /api/users/<user_id>/ai-prompts`
- `PUT /api/users/<user_id>/ai-prompts/<method_name>`

## Auth Rules
- All `/api/users/<user_id>/...` endpoints require `Authorization: Bearer <token>`.
- `user_id` in path must match token owner; cross-user access is blocked (`403`).
- `GET /api/users` now returns only current authenticated user data.
