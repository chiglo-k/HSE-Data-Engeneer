

-- Хаб заказов: центральная сущность для группировки продаж
CREATE TABLE dv.h_order ( 
    hk_order CHAR(32) NOT NULL,            
    order_id VARCHAR(50) NOT NULL,           
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки записи
    record_source VARCHAR(50) NOT NULL,      -- Источник данных
    CONSTRAINT h_order_pk PRIMARY KEY (hk_order),
    CONSTRAINT h_order_order_id_uk UNIQUE (order_id)
) 
DISTRIBUTED BY (hk_order)                   
PARTITION BY RANGE (load_date_ts);          



-- Хаб продуктов: уникальные комбинации категория+подкатегория
CREATE TABLE dv.h_product (
    hk_product CHAR(32) NOT NULL,           
    category VARCHAR(100) NOT NULL,          
    sub_category VARCHAR(100) NOT NULL,      
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки
    record_source VARCHAR(50) NOT NULL,      -- Источник данных
    CONSTRAINT h_product_pk PRIMARY KEY (hk_product),
    CONSTRAINT h_product_cat_subcat_uk UNIQUE (category, sub_category)
) 
DISTRIBUTED BY (hk_product)
PARTITION BY RANGE (load_date_ts);



-- Хаб географии: трехуровневая иерархия страна-штат-город
CREATE TABLE dv.h_geography (
    hk_geography CHAR(32) NOT NULL,          
    country VARCHAR(100) NOT NULL,           
    state VARCHAR(100) NOT NULL,             
    city VARCHAR(100) NOT NULL,              
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки
    record_source VARCHAR(50) NOT NULL,      -- Источник данных
    CONSTRAINT h_geography_pk PRIMARY KEY (hk_geography),
    CONSTRAINT h_geography_location_uk UNIQUE (country, state, city)
) 
DISTRIBUTED BY (hk_geography)
PARTITION BY RANGE (load_date_ts);



-- Хаб сегментов: классификация клиентов для маркетингового анализа
CREATE TABLE dv.h_segment (
    hk_segment CHAR(32) NOT NULL,            
    segment VARCHAR(50) NOT NULL,            -- Сегмент клиентов (Consumer, Corporate, Home Office)
    load_date_ts TIMESTAMP NOT NULL,         -- Дата первой загрузки
    record_source VARCHAR(50) NOT NULL,      -- Источник данных
    CONSTRAINT h_segment_pk PRIMARY KEY (hk_segment),
    CONSTRAINT h_segment_segment_uk UNIQUE (segment)
) 
DISTRIBUTED BY (hk_segment)
PARTITION BY RANGE (load_date_ts);

