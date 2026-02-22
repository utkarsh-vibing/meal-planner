# MealMind API (working local prototype)

This repository now contains a **runnable backend API prototype** with no external framework dependency.

## What is implemented
- User creation
- Meal creation/listing with normalized ingredient names
- Weekly meal plan generation (idempotent per user+week)
- Meal slot updates
- Grocery list aggregation from the latest generated plan
- HTTP tests covering health and end-to-end flow

## What is not complete yet
- Mobile app UI
- Authentication/authorization
- AI planning/deduplication/voice agent
- Advanced grocery scopes (`tomorrow` vs `this_week` vs `next_week` logic differences)
- Migrations and production-grade deployment setup

## Run
```bash
python -m app.main
```
Server starts at: `http://127.0.0.1:8000`

## Test
```bash
python -m unittest -q
```

## Example API calls
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users -H 'content-type: application/json' -d '{"name":"Asha"}'
curl -X POST http://127.0.0.1:8000/api/v1/meals -H 'content-type: application/json' -d '{"user_id":1,"name":"Paneer Bowl","ingredients":[{"ingredient_name":"paneer","quantity":2,"unit":"cup"}]}'
curl -X POST http://127.0.0.1:8000/api/v1/meal-plan/generate -H 'content-type: application/json' -d '{"user_id":1,"week_start_date":"2026-02-16"}'
curl -X POST http://127.0.0.1:8000/api/v1/grocery-list -H 'content-type: application/json' -d '{"user_id":1,"scope":"this_week"}'
```
