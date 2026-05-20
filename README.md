# FitDiscipline Backend (Flask + MySQL)

Backend ini mengikuti `guidance.md` sebagai source of truth untuk schema dan flow utama:
- onboarding
- plans (workout/meal)
- daily tracking (weight, meal, workout, day score)
- review trigger mingguan/bulanan
- AI prompt configuration

## 1. Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Environment variable opsional:
- `MYSQL_HOST` (default: `127.0.0.1`)
- `MYSQL_PORT` (default: `3306`)
- `MYSQL_USER` (default: `root`)
- `MYSQL_PASSWORD` (default: empty)
- `MYSQL_DB` (default: `healthapp`)
- `APP_HOST` (default: `0.0.0.0`)
- `APP_PORT` (default: `5000`)
- `DEBUG` (default: `true`)

## 2. Run App

```bash
python app.py
```

## 3. Initialize Database Schema

```bash
curl -X POST http://localhost:5000/api/system/init-db
```

Schema source: `db/schema.sql`.

## 4. Core API Endpoints

System:
- `GET /api/system/health/db`
- `POST /api/system/init-db`

Users:
- `POST /api/users`
- `GET /api/users`
- `GET /api/users/<user_id>`
- `PATCH /api/users/<user_id>`
- `POST /api/users/onboarding`
- `PUT /api/users/<user_id>/preferences`
- `GET /api/users/<user_id>/preferences`
- `POST /api/users/<user_id>/food-preferences`
- `GET /api/users/<user_id>/food-preferences`
- `DELETE /api/users/<user_id>/food-preferences/<preference_id>`

Plans:
- `POST /api/users/<user_id>/workout-plans`
- `GET /api/users/<user_id>/workout-plans`
- `POST /api/users/<user_id>/workout-plans/<plan_id>/activate`
- `POST /api/users/<user_id>/meal-plans`
- `GET /api/users/<user_id>/meal-plans`
- `POST /api/users/<user_id>/meal-plans/<plan_id>/activate`
- `GET /api/users/<user_id>/active-program`

Tracking:
- `POST /api/users/<user_id>/weight-logs`
- `GET /api/users/<user_id>/weight-logs`
- `POST /api/users/<user_id>/workout-sessions`
- `GET /api/users/<user_id>/workout-sessions`
- `POST /api/users/<user_id>/meal-logs`
- `GET /api/users/<user_id>/meal-logs`
- `POST /api/users/<user_id>/fitness-capabilities`
- `GET /api/users/<user_id>/fitness-capabilities`
- `PUT /api/users/<user_id>/day-scores/<score_date>`
- `GET /api/users/<user_id>/day-scores`

Review:
- `GET /api/users/<user_id>/reviews/weekly`
- `POST /api/users/<user_id>/reviews/monthly/check-trigger`
- `POST /api/users/<user_id>/reviews/monthly/mark-done`

AI Prompt Config:
- `GET /api/users/<user_id>/ai-prompts`
- `PUT /api/users/<user_id>/ai-prompts/<method_name>`

## 5. Notes

- `fitness_capabilities` diimplementasi append-only (insert snapshot baru, tidak update row lama).
- `food_preferences` pakai soft delete lewat `deleted_at`.
- `day_scores` pakai upsert (`UNIQUE(user_id, score_date)`).
- Aktivasi plan akan archive plan active sebelumnya.

## 6. Architecture Rules

- SQL hanya di `repositories/`.
- Blueprint hanya handle HTTP concern (parse request + return response).
- Business logic di `services/`.
- Validation schema di `schemas/`.
- Utility lintas domain di `core/`.
