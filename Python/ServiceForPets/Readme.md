## Микросервис для ветклиники

### Функции:

1. Запись собак на прием;
2. Получение списка собак;
3. Получение собаки по id;
4. Получение собак по типу;
5. Обновление собаки по id.

### Запуск микросервиса:

`uvicorn main:app --reload`

#### Документация API:
 Эндпоинты:

    GET / - Корневой эндпоинт
    GET /dog - Список всех собак или фильтрация по типу
    POST /dog - Создание новой собаки
    PATCH /dog/{pk} - Обновление существующей собаки
    GET /dog/{pk} - Получение собаки по первичному ключу

Структура кода

    DogType enum для пород собак
    Dog Pydantic модель для данных собак
    Временные базы данных для собак и постов
    FastAPI маршруты для различных операций

#### Примеры Использования:
  
`https://microapp-vet.onrender.com/dog` -- Просмотр всех животных БД

`curl -X GET https://microapp-vet.onrender.com/dog?kind=bulldog` - Фильтрация по породе собаки 

`curl -X POST https://microapp-vet.onrender.com/dog -H "Content-Type: application/json" -d '{"name": "Buddy", "pk": 7, "kind": "terrier"}'` - Добавить нового клиента

