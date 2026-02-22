# MealMind API scaffold

Initial backend scaffold for the MealMind MVP described in the PRD.

## Included

- FastAPI app with versioned API routes (`/api/v1`)
- SQLModel-backed data models for core PRD entities
- Starter endpoints for meals, meal plans, slot updates, and grocery list generation
- Basic deterministic meal-plan generator service and grocery summarizer
- Healthcheck test

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```

## Next steps

1. Add proper migrations (Alembic) and switch default local DB to Postgres.
2. Add auth + user scoping from token instead of `user_id` query/body fields.
3. Replace deterministic planner with AI constraint-aware generation.
4. Add ingredient alias model and semantic dedupe workflow.
5. Expand grocery list logic by scope (tomorrow/this_week/next_week).
