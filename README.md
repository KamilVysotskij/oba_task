# OBA Task
Organization, building, activity
## Подготовка

Нужно:

- Docker и Docker Compose
- `uv`
- Python `3.12`

Создай `.env`:

```bash
cp .env.example .env
```

## Запуск через Docker

Основной способ запуска:

```bash
make up
```

После запуска доступны:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Healthcheck: [http://localhost:8000/health](http://localhost:8000/health)

Остановка:

```bash
make down
```

Логи приложения:

```bash
make logs
```

Логи PostgreSQL:

```bash
make logs c=db
```

Перезапуск контейнера приложения:

```bash
make restart
```

Перезапуск контейнера БД:

```bash
make restart c=db
```

Миграции:

```bash
make migrate
```

Создать новую миграцию:

```bash
make migration-create message="add organizations index"
```

Shell приложения:

```bash
make app-shell
```

Shell PostgreSQL:

```bash
make db-shell
```

Важно: `make migrate`, `make migration-create`, `make app-shell`, `make db-shell`,
`make ruff-check` и `make ruff-format` работают через `docker compose exec`,
поэтому сначала нужен `make up`.

## Тесты

Установи зависимости:

```bash
uv sync --dev
```

Запуск тестов:

```bash
make test
```

Если нужно, можно переопределить тестовую БД:

```bash
export TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/oba_test
```

## Ruff

Проверка:

```bash
make ruff-check
```

Автоисправление и форматирование:

```bash
make ruff-format
```

## Локальный запуск без Docker

1. Подними PostgreSQL отдельно.
2. Создай `.env`.
3. Установи зависимости:

```bash
uv sync --dev
```

4. Прогони миграции:

```bash
uv run python -m alembic upgrade head
```

5. Заполни БД данными:

```bash
uv run seed-db
```

6. Запусти приложение:

```bash
uv run python -m uvicorn app.main:app --reload
```
