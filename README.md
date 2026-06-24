# Booking Service

Веб-сервис для автоматизации бронирования переговорных комнат в коворкинге.

## Функциональность

- Регистрация и аутентификация пользователей (JWT + HttpOnly cookies)
- Управление ролями: сотрудник (client) и администратор (admin)
- Просмотр доступных временных слотов для всех комнат на выбранную дату
- Создание и отмена собственных бронирований
- Администратор может просматривать и отменять любые бронирования
- Защита от двойного бронирования (unique partial index)
- RS256 JWT с ограниченным сроком действия (15 минут)

## Технологии

- **Python 3.12** + **FastAPI**
- **PostgreSQL** (через SQLAlchemy async + asyncpg) или **SQLite** (через aiosqlite)
- **Alembic** для миграций
- **Docker** + **docker-compose**
- **Pytest** для тестов (unit + integration)
- **Poetry** для управления зависимостями

## Быстрый старт

### Запуск через Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/diggorpo/booking_service.git
cd booking_service

# Создать .env файл (пример)
cp .env.example .env

# Запустить сервис с PostgreSQL
docker compose up --build
```

После запуска сервис будет доступен по адресу: http://localhost:8000

Документация API (Swagger): http://localhost:8000/docs

### Запуск локально с SQLite

```bash
# Установить зависимости
poetry install

# Запустить миграции
poetry run alembic upgrade head

# Запустить сервер
poetry run uvicorn main:app --reload
```

### Запуск тестов

```bash
poetry run pytest -v
```

## API Endpoints

### Аутентификация

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/api/v1/auth/register` | Регистрация нового пользователя | Все |
| POST | `/api/v1/auth/login` | Вход в систему | Все |
| POST | `/api/v1/auth/logout` | Выход из системы | Авторизованные |

### Слоты

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/v1/slots/availability` | Получить доступные слоты за период | Авторизованные |

Параметры:
- `room_id` (int, опционально) — фильтр по комнате
- `start_date` (date, опционально) — начальная дата (по умолчанию: сегодня)
- `end_date` (date, опционально) — конечная дата (по умолчанию: через 14 дней)

### Бронирования (сотрудник)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/v1/bookings/` | Получить свои бронирования | Авторизованные |
| POST | `/api/v1/bookings/{slot_id}` | Создать бронирование на слот | Авторизованные |
| PATCH | `/api/v1/bookings/{booking_id}/cancel` | Отменить своё бронирование | Владелец |

### Администрирование (администратор)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/v1/admin/booking/` | Получить все бронирования | Администратор |
| PATCH | `/api/v1/admin/booking/{booking_id}/cancel` | Отменить любое бронирование | Администратор |

## Примеры работы с API

### Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Иван",
    "last_name": "Петров",
    "email": "ivan@example.com",
    "phone_number": "+79991112233",
    "password": "securepassword123"
  }'
```

Ответ:
```json
{
  "id": 1,
  "first_name": "Иван",
  "last_name": "Петров",
  "email": "ivan@example.com",
  "phone_number": "+79991112233",
  "role": {
    "id": 3,
    "name": "client"
  }
}
```

### Вход в систему

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "password": "securepassword123"
  }'
```

Ответ приходит с HttpOnly cookie `Authorization`, содержащей JWT-токен.

### Создание бронирования

```bash
curl -X POST "http://localhost:8000/api/v1/bookings/1?date=2026-07-01" \
  -b "Authorization=<token>"
```

### Получение доступных слотов

```bash
curl -X GET "http://localhost:8000/api/v1/slots/availability?start_date=2026-07-01&end_date=2026-07-03" \
  -b "Authorization=<token>"
```

Ответ:
```json
[
  {
    "date": "2026-07-01",
    "free_slots": [
      {
        "id": 1,
        "start_time": "09:00:00",
        "end_time": "11:00:00"
      },
      {
        "id": 2,
        "start_time": "11:00:00",
        "end_time": "13:00:00"
      }
    ]
  }
]
```

### Получение своих бронирований

```bash
curl -X GET http://localhost:8000/api/v1/bookings/ \
  -b "Authorization=<token>"
```

### Отмена бронирования

```bash
curl -X PATCH http://localhost:8000/api/v1/bookings/1/cancel \
  -b "Authorization=<token>"
```

### Администрирование (требуется роль admin)

```bash
# Получить все бронирования
curl -X GET http://localhost:8000/api/v1/admin/booking/ \
  -b "Authorization=<token>"

# Отменить любое бронирование
curl -X PATCH http://localhost:8000/api/v1/admin/booking/1/cancel \
  -b "Authorization=<token>"
```

## Структура проекта

```
booking_service/
├── api/
│   └── api_v1/
│       ├── auth/              # Аутентификация и пользователи
│       │   ├── handler.py     # JWT encode/decode, хеширование паролей
│       │   ├── schemas.py     # Pydantic схемы
│       │   ├── service.py     # Бизнес-логика
│       │   ├── utils.py       # Вспомогательные функции
│       │   └── views.py       # Эндпоинты
│       ├── bookings/          # Бронирования
│       │   ├── admin/         # Администрирование бронирований
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── views.py
│       └── slots/             # Временные слоты
│           ├── schemas.py
│           ├── service.py
│           └── views.py
├── core/
│   ├── config.py              # Настройки приложения
│   └── infrastructure/
│       └── db/
│           ├── db_helper.py   # Подключение к БД
│           ├── models/        # SQLAlchemy модели
│           └── repositories/  # Репозитории (слой доступа к данным)
├── tests/
│   ├── unit/                  # Юнит-тесты (6 файлов)
│   └── integration/           # Интеграционные тесты (5 файлов)
├── alembic/                   # Миграции БД
├── scripts/                   # Вспомогательные скрипты
├── docker-compose.yml         # Docker Compose (PostgreSQL + приложение)
├── Dockerfile                 # Dockerfile для сборки образа
├── entrypoint.sh              # Точка входа в контейнер
├── pyproject.toml             # Зависимости (Poetry)
└── README.md
```

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DB_URL` | URL подключения к БД | `postgresql+asyncpg://postgres:password@db:5432/booking_service` |

Для запуска с SQLite (локально без Docker):
```bash
export DB_URL="sqlite+aiosqlite:///./db.sqlite3"