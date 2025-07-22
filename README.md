# Study Platform

Платформа для самообучения студентов на Django + DRF

## Возможности
- Регистрация и аутентификация пользователей (JWT)
- Подтверждение email при регистрации (асинхронно через Celery)
- Роли: Администратор, Преподаватель, Студент
- CRUD для курсов, материалов, тестов, вопросов, ответов
- Прохождение тестов и автоматическая проверка
- Swagger-документация API
- Админ-панель Django
- Полное покрытие автотестами (pytest)
- Асинхронные задачи через Celery + Redis
- Production-ready: Docker Compose, Nginx, .env

## Установка и запуск

1. Клонируйте репозиторий и перейдите в папку проекта:
   ```bash
   git clone <repo_url>
   cd self_study_project
   ```
2. Создайте файл `.env` на основе `.env.sample` и заполните переменные:
   ```bash
   cp .env.sample .env
   # отредактируйте значения (секреты, пароли, email и т.д.)
   ```
3. Соберите и запустите проект через Docker Compose:
   ```bash
   docker-compose up --build
   ```
   Это поднимет сервисы: db, redis, web (Django), celery, celery-beat, nginx.
4. Для доступа к приложению:
   - Swagger: [http://localhost/swagger/](http://localhost/swagger/)
   - Админка: [http://localhost/admin/](http://localhost/admin/)

## Переменные окружения
- Все чувствительные данные и настройки берутся из `.env` (см. `.env.sample`).
- Используется пакет `django-environ` для удобной работы с переменными.
- Не коммитьте `.env` в репозиторий!

## Email-подтверждение
- После регистрации на указанный email отправляется письмо с подтверждением (асинхронно через Celery).
- Для разработки используется console backend (письма выводятся в консоль).
- Для production настройте SMTP backend и переменные EMAIL_HOST, EMAIL_PORT и т.д.
- Подтверждение email — GET-запрос на `/api/confirm-email/<token>/`.

## Асинхронные задачи
- Celery worker и beat запускаются как отдельные сервисы в Docker Compose.
- Redis используется как брокер.

## Production
- Для production используйте SMTP для email, DEBUG=False, секретные ключи и пароли в .env.
- Nginx проксирует запросы к Gunicorn (web) и отдаёт статику/медиа.
- Для деплоя используйте CI/CD pipeline (см. .github/workflows/ci.yml).

## Тестирование

Для запуска всех автотестов:
```bash
pytest -v
```
Для покрытия:
```bash
pytest --cov=. --cov-report=term-missing -v
```

## Документация API
- Swagger UI: [http://localhost/swagger/](http://localhost/swagger/)
- Redoc: [http://localhost/redoc/](http://localhost/redoc/)
- Подробности — см. API.md

## Основные роли и права
- **Администратор**: полный доступ ко всем функциям, управление пользователями
- **Преподаватель**: создание и управление своими курсами, материалами, тестами
- **Студент**: просмотр материалов, прохождение тестов

## Примеры основных эндпоинтов
- Регистрация: `POST /api/register/` (username, password, email)
- JWT-логин: `POST /api/login/` (username, password)
- Подтверждение email: `GET /api/confirm-email/<token>/`
- Курсы: `GET/POST /api/courses/`
- Материалы: `GET/POST /api/materials/`
- Тесты: `GET/POST /api/tests/`
- Прохождение теста: `POST /api/tests/<test_id>/check/` (answers: {question_id: answer_id})

## Структура проекта
- users — пользователи, роли, регистрация, аутентификация, email-подтверждение
- courses — курсы и материалы
- tests — тесты, вопросы, ответы, результаты

---

**Проект соответствует стандартам PEP8, покрыт тестами и готов к развертыванию!** 