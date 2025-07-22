# API Документация

## Аутентификация и регистрация

### Регистрация
- **POST** `/api/register/`
- **Request:**
  ```json
  {
    "username": "user1",
    "password": "pass1234",
    "email": "user1@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "role": "student"
  }
  ```
- **Особенности:**
  - Email обязателен.
  - После регистрации на email приходит письмо с подтверждением (асинхронно через Celery).
  - Без подтверждения email доступ к некоторым функциям может быть ограничен.

### Подтверждение email
- **GET** `/api/confirm-email/<token>/`
- **Response (успех):**
  ```json
  { "detail": "Email подтвержден!" }
  ```
- **Response (ошибка):**
  ```json
  { "detail": "Not found." }
  ```

### JWT-логин
- **POST** `/api/login/`
- **Request:**
  ```json
  {
    "username": "user1",
    "password": "pass1234"
  }
  ```
- **Response:**
  ```json
  {
    "refresh": "...",
    "access": "..."
  }
  ```

---

## Курсы

### Получить список курсов
- **GET** `/api/courses/`
- **Response:**
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Course 1",
        "description": "desc",
        "owner": 2,
        "materials": [ ... ]
      }
    ]
  }
  ```

### Создать курс (только преподаватель/админ)
- **POST** `/api/courses/`
- **Request:**
  ```json
  {
    "title": "Course 1",
    "description": "desc"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "title": "Course 1",
    "description": "desc",
    "owner": 2,
    "materials": []
  }
  ```

---

## Материалы

### Получить список материалов
- **GET** `/api/materials/`

### Создать материал (только преподаватель/админ)
- **POST** `/api/materials/`
- **Request:**
  ```json
  {
    "course": 1,
    "title": "Material 1",
    "content": "text"
  }
  ```

---

## Тесты и вопросы

### Получить список тестов
- **GET** `/api/tests/`

### Создать тест (только преподаватель/админ)
- **POST** `/api/tests/`
- **Request:**
  ```json
  {
    "material": 1,
    "title": "Test 1"
  }
  ```

### Получить список вопросов
- **GET** `/api/questions/`

### Создать вопрос (только преподаватель/админ)
- **POST** `/api/questions/`
- **Request:**
  ```json
  {
    "test": 1,
    "text": "2+2?"
  }
  ```

### Получить список ответов
- **GET** `/api/answers/`

### Создать ответ (только преподаватель/админ)
- **POST** `/api/answers/`
- **Request:**
  ```json
  {
    "question": 1,
    "text": "4",
    "is_correct": true
  }
  ```

---

## Прохождение теста

### Проверить тест
- **POST** `/api/tests/<test_id>/check/`
- **Request:**
  ```json
  {
    "answers": {
      "<question_id>": <answer_id>
    }
  }
  ```
- **Response:**
  ```json
  {
    "score": 1.0,
    "test_result_id": 5
  }
  ```

---

## Прочее
- Все запросы (кроме регистрации и логина) требуют JWT-токен в заголовке:
  ```
  Authorization: Bearer <access_token>
  ```
- Пагинация, поиск, сортировка поддерживаются для всех списков (параметры: `?search=`, `?ordering=`)
- Полная схема доступна в Swagger: `/swagger/` 