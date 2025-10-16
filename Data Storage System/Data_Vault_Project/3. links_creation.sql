

CREATE TABLE dv.l_sales (
    lhk_sales CHAR(32) NOT NULL,            
    hk_order CHAR(32) NOT NULL,              -- FK к хабу заказов
    hk_product CHAR(32) NOT NULL,            -- FK к хабу продуктов
    hk_geography CHAR(32) NOT NULL,          -- FK к хабу географии
    hk_segment CHAR(32) NOT NULL,            -- FK к хабу сегментов
    load_date_ts TIMESTAMP NOT NULL,         -- Дата загрузки 
    record_source VARCHAR(50) NOT NULL,      -- Источник данных
    CONSTRAINT l_sales_pk PRIMARY KEY (lhk_sales),
    CONSTRAINT l_sales_h_order_fk 
        FOREIGN KEY (hk_order) REFERENCES dv.h_order (hk_order),
    CONSTRAINT l_sales_h_product_fk 
        FOREIGN KEY (hk_product) REFERENCES dv.h_product (hk_product),
    CONSTRAINT l_sales_h_geography_fk 
        FOREIGN KEY (hk_geography) REFERENCES dv.h_geography (hk_geography),
    CONSTRAINT l_sales_h_segment_fk 
        FOREIGN KEY (hk_segment) REFERENCES dv.h_segment (hk_segment)
) 
DISTRIBUTED BY (lhk_sales)                 
PARTITION BY RANGE (load_date_ts);