# Сервисы TODO и Short URL

Этот репозиторий содержит два сервиса:

1. **TODO-сервис**: Реализует CRUD-операции для списка задач с хранением данных в SQLite.
2. **Сервис сокращения URL**: Позволяет создавать короткие ссылки для длинных URL и хранит данные в SQLite.

## Docker

### TODO-сервис

#### Dockerfile

- **FROM python:3.9-slim**: Базовый образ с Python.
- **WORKDIR /app**: Рабочая директория.
- **COPY requirements.txt .** и **RUN pip install**: Установка зависимостей.
- **COPY . .**: Копирование кода.
- **VOLUME ["/app/data"]**: Объявление тома.
- **CMD**: Запуск через uvicorn.

#### Сборка и запуск

1. **Сборка образа**:

   ```bash
   docker build -t todo-sqlite:todo .
   ```

2. **Создание тома**:

   ```bash
   docker volume create todo_data
   ```

3. **Запуск контейнера**:

   ```bash
   docker run -d -p 0000:80 -v todo_data:/app/data todo-sqlite:todo
   ```

   Сервис доступен по адресу: `http://localhost:80`

### Команды для тестирования

- **Создание задачи**:

  ```bash
  curl -X POST http://localhost:80/items -H "Content-Type: application/json" -d '{"title":"some action","description":"some production","completed":false}'
  ```

- **Получение всех задач**:

  ```bash
  curl http://localhost:80/items/
  ```

- **Обновление задачи**:

  ```bash
  curl -X PUT http://localhost:80/items/1 -H "Content-Type: application/json" -d '{"title":"some action","description":"some production","completed":true}'
  ```

- **Удаление задачи**:

  ```bash
  curl -X DELETE http://localhost:80/items/id
  ```

### Short URL

- **main.py**: Основной файл приложения.
- **models.py**: Модель для таблицы.
- **database.py**: Подключение к базе данных.
- **Dockerfile**: Описание образа Docker.

#### Dockerfile

- **FROM python:3.9-slim**: Легкий образ Python.
- **WORKDIR /app**: Рабочая директория.
- **COPY requirements.txt .** и **RUN pip install**: Установка зависимостей.
- **COPY . .**: Копирование файлов.
- **VOLUME ["/app/data"]**: Объявление тома.
- **CMD**: Запуск через uvicorn.

1. **Сборка образа**:

```bash
docker build -t shorturl:shorturl .
```
2. **Запуск контейнера**:

```bash
docker run -d -p 0000:80 shorturl:shorturl
```
