

-- Географические атрибуты: изменяемые свойства локаций
CREATE TABLE dv.s_geography (
    hk_geography CHAR(32) NOT NULL,          -- FK к хабу географии
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки 
    postal_code VARCHAR(20),                 -- Почтовый индекс (может изменяться)
    region VARCHAR(100),                     -- Регион (??)
    record_source VARCHAR(50) NOT NULL,     
    CONSTRAINT s_geography_pk PRIMARY KEY (hk_geography, load_date_ts),
    CONSTRAINT s_geography_h_geography_fk 
        FOREIGN KEY (hk_geography) REFERENCES dv.h_geography (hk_geography)
) 
DISTRIBUTED BY (hk_geography)               
PARTITION BY RANGE (load_date_ts);



-- Атрибуты доставки: логистика
CREATE TABLE dv.s_order_shipping (
    hk_order CHAR(32) NOT NULL,              -- FK к хабу заказов
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки 
    ship_mode VARCHAR(50),                   -- Способ доставки (Standard, Second Class, etc.)
    record_source VARCHAR(50) NOT NULL,      
    CONSTRAINT s_order_shipping_pk PRIMARY KEY (hk_order, load_date_ts),
    CONSTRAINT s_order_shipping_h_order_fk 
        FOREIGN KEY (hk_order) REFERENCES dv.h_order (hk_order)
) 
DISTRIBUTED BY (hk_order)                   
PARTITION BY RANGE (load_date_ts);



-- Метрики продаж: бизнес-показатели 
CREATE TABLE dv.s_sales_metrics (
    lhk_sales CHAR(32) NOT NULL,             -- FK к связи продаж
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки 
    sales DECIMAL(15,4),                     -- Сумма продаж 
    quantity INTEGER,                        -- Количество товара
    discount DECIMAL(5,3),                   -- Размер скидки (в анализе используют 3 числа после запятой, особенно когда кто-то денежный поток анализирует)
    profit DECIMAL(15,3),                    -- Прибыль (см. скидку)
    record_source VARCHAR(50) NOT NULL,      
    CONSTRAINT s_sales_metrics_pk PRIMARY KEY (lhk_sales, load_date_ts),
    CONSTRAINT s_sales_metrics_l_sales_fk 
        FOREIGN KEY (lhk_sales) REFERENCES dv.l_sales (lhk_sales),
    -- Бизнес-правила для обеспечения качества данных
    CONSTRAINT s_sales_metrics_sales_positive CHECK (sales >= 0),
    CONSTRAINT s_sales_metrics_quantity_positive CHECK (quantity > 0),
    CONSTRAINT s_sales_metrics_discount_range CHECK (discount >= 0 AND discount <= 1)
) 
DISTRIBUTED BY (lhk_sales)                 
PARTITION BY RANGE (load_date_ts);

