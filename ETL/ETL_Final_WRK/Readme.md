# Итоговое задание ETL

## Задание 1: Работа с Yandex DataTransfer

Требуется перенести данные из Managed Service for YDB в объектное хранилище Object Storage. 
Выполнить необходимо с использованием сервиса Data Transfer.


1.	**Создать БД Yandex DataBase:**


```SQL
CREATE TABLE it_salary_new(
    id UUID NOT NULL,
    job_title Utf8,
    salary_usd Uint32,
    experience_level Utf8,
    company_location Utf8,
    posting_date Date,
    PRIMARY KEY (id)
);
```

2.	**Подготовить данные:**

Для подготовки данных и создание датасета используем создание нескольких таблиц с данными, 
чтобы затем использовать их для подготовки данных в основной таблице.

<details>
<summary>SQL скрипт подготовки данных</summary>

```SQL
CREATE TABLE temp_job_titles(
  id Uint32,
  value Utf8,
  PRIMARY KEY(id)
);


INSERT INTO temp_job_titles(id, value) VALUES
(1, 'Software Engineer'),
(2, 'Data Scientist'),
(3, 'DevOps Engineer'),
(4, 'Product Manager'),
(5, 'QA Engineer'),
(6, 'Frontend Developer'),
(7, 'Backend Developer'),
(8, 'Full Stack Developer'),
(9, 'Data Engineer'),
(10, 'ML Engineer');


CREATE TABLE temp_experience_levels(
  id Uint32,
  value Utf8,
  PRIMARY KEY(id)
);

INSERT INTO temp_experience_levels(id, value) VALUES 
    (1, 'Junior'),
    (2, 'Middle'),
    (3, 'Senior'),
    (4, 'Lead'),
    (5, 'Principal');


CREATE TABLE temp_locations(
  id Uint32,
  value Utf8,
  PRIMARY KEY(id)
);

INSERT INTO temp_locations(id, value) VALUES 
    (1, 'USA'),
    (2, 'Germany'),
    (3, 'UK'),
    (4, 'Canada'),
    (5, 'India'),
    (6, 'Japan'),
    (7, 'Australia'),
    (8, 'France'),
    (9, 'Spain'),
    (10, 'Russia'),
    (11, 'China'),
    (12, 'Brazil'),
    (13, 'Netherlands'),
    (14, 'Sweden'),
    (15, 'Singapore'),
    (16, 'Italy'),
    (17, 'Poland'),
    (18, 'UAR'),
    (19, 'Egypt'),
    (20, 'Switzerland');
```
</details>
Затем приступаем к заполнению основной таблицы, данные в которой будут созданы рандомно в размере 1000 строк,
это поможет нагенерировать необходимый объяем тестовых данных, не копируя и вставляя код, а исполняя его столько раз сколько необходимо. 

<details>
<summary>SQL скрипт Insert Values</summary>
    
```SQL
INSERT INTO it_salary_new (id, job_title, salary_usd, experience_level, company_location)
SELECT 
    RANDOM_UUID(j.id * 10000 + e.id * 1000 + l.id) AS id,  -- Использование комбинации значений как параметра
    j.value AS job_title,
    CAST(50000 + (j.id * 10000) AS Uint32) AS salary_usd,
    e.value AS experience_level,
    l.value AS company_location
FROM 
    temp_job_titles AS j
    CROSS JOIN temp_experience_levels AS e
    CROSS JOIN temp_locations AS l
LIMIT 1000;
```
</details>

3. Создать трансфер в **Object Storage:**
   
![](1st%20task/Screen/transfer_go.png)

![](1st%20task/Screen/result_transfer.png)
   












