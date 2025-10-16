# Data Vault модель для Superstore

## Структура данных

**Исходные данные:** Ship Mode, Segment, Country, City, State, Postal Code, Region, Category, Sub-Category, Sales, Quantity, Discount, Profit [https://www.kaggle.com/datasets/roopacalistus/superstore] 

## Архитектура хранилища данных

### Хабы (Hubs)

- **H_ORDER** - Хаб заказов

       Содержит уникальные идентификаторы заказов для группировки связанных продаж.

- **H_PRODUCT** - Хаб продуктов

        Хранит уникальные комбинации категорий и подкатегорий продуктов.

- **H_GEOGRAPHY** - Хаб географии

        Содержит уникальные географические локации (страна-штат-город).

- **H_SEGMENT** - Хаб сегментов

        Хранит уникальные сегменты клиентов для маркетингового анализа.

- **L_SALES** - Связь продаж

        Основная связь, объединяющая все измерения продаж для многомерного анализа.

### Связи (Links)

- **L_SALES** - Связь продаж

        Основная связь, объединяющая все измерения продаж для многомерного анализа.

### Спутники (Satellites)

- **S_GEOGRAPHY** - Спутник географических атрибутов

        Хранит изменяемые атрибуты географических локаций с историей изменений.

- **S_ORDER_SHIPPING** - Спутник атрибутов доставки

        Содержит информацию о способах доставки заказов с возможностью отслеживания изменений.

- **S_SALES_METRICS** - Спутник метрик продаж

        Хранит ключевые бизнес-метрики продаж с поддержкой исторических изменений.





```mermaid
graph TB
    %% Исходные данные
    subgraph "Superstore Dataset"
        DATA[Ship Mode, Segment, Country, City, State<br/>Postal Code, Region, Category, Sub-Category<br/>Sales, Quantity, Discount, Profit]
    end
    
    %% Хабы
    subgraph "HUBS"
        H_ORDER[H_ORDER<br/>order_id]
        H_PRODUCT[H_PRODUCT<br/>category + sub_category]
        H_GEOGRAPHY[H_GEOGRAPHY<br/>country + state + city]
        H_SEGMENT[H_SEGMENT<br/>segment]
    end
    
    %% Связи
    subgraph "LINKS"
        L_SALES[L_SALES<br/>Main sales relationship]
    end
    
    %% Спутники
    subgraph "SATELLITES"
        S_GEOGRAPHY[S_GEOGRAPHY<br/>postal_code, region]
        S_SHIPPING[S_ORDER_SHIPPING<br/>ship_mode]
        S_METRICS[S_SALES_METRICS<br/>sales, quantity, discount, profit]
    end
    
    %% Связи
    DATA --> H_ORDER
    DATA --> H_PRODUCT
    DATA --> H_GEOGRAPHY
    DATA --> H_SEGMENT
    
    H_ORDER --> L_SALES
    H_PRODUCT --> L_SALES
    H_GEOGRAPHY --> L_SALES
    H_SEGMENT --> L_SALES
    
    H_GEOGRAPHY --> S_GEOGRAPHY
    H_ORDER --> S_SHIPPING
    L_SALES --> S_METRICS
```

## Структура таблиц

**Оптимизация типов данных**

- CHAR(32) для hash ключей - фиксированная длина для оптимальной производительности JOIN операций
- DECIMAL(15,4) для финансовых данных - высокая точность без потери производительности
- DECIMAL(5,4) для скидок - точное представление процентных значений
- VARCHAR с оптимальными размерами - баланс между производительностью и гибкостью

**Ограничения целостности данных**

- PRIMARY KEY на всех таблицах для уникальности
- FOREIGN KEY для обеспечения ссылочной целостности
- UNIQUE ограничения на бизнес-ключи
- CHECK ограничения для бизнес-правил (положительные значения, диапазоны)


```mermaid
erDiagram
    H_ORDER {
        char hk_order PK
        varchar order_id UK
        timestamp load_date_ts
        varchar record_source
    }
    
    H_PRODUCT {
        char hk_product PK
        varchar category UK
        varchar sub_category UK
        timestamp load_date_ts
        varchar record_source
    }
    
    H_GEOGRAPHY {
        char hk_geography PK
        varchar country UK
        varchar state UK
        varchar city UK
        timestamp load_date_ts
        varchar record_source
    }
    
    H_SEGMENT {
        char hk_segment PK
        varchar segment UK
        timestamp load_date_ts
        varchar record_source
    }
    
    L_SALES {
        char lhk_sales PK
        char hk_order FK
        char hk_product FK
        char hk_geography FK
        char hk_segment FK
        timestamp load_date_ts
        varchar record_source
    }
    
    S_GEOGRAPHY {
        char hk_geography PK
        timestamp load_date_ts PK
        varchar postal_code
        varchar region
        varchar record_source
    }
    
    S_ORDER_SHIPPING {
        char hk_order PK
        timestamp load_date_ts PK
        varchar ship_mode
        varchar record_source
    }
    
    S_SALES_METRICS {
        char lhk_sales PK
        timestamp load_date_ts PK
        decimal sales
        integer quantity
        decimal discount
        decimal profit
        varchar record_source
    }
    
    H_ORDER ||--o{ L_SALES : contains
    H_PRODUCT ||--o{ L_SALES : contains
    H_GEOGRAPHY ||--o{ L_SALES : contains
    H_SEGMENT ||--o{ L_SALES : contains
    
    H_GEOGRAPHY ||--o{ S_GEOGRAPHY : describes
    H_ORDER ||--o{ S_ORDER_SHIPPING : describes
    L_SALES ||--o{ S_SALES_METRICS : contains
```
