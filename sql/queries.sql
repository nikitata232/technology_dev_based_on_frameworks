-- ==========================================
-- КиноПлан: SQL-запросы проекта
-- ==========================================
-- Проверка в SQLite CLI из корня проекта:
--     sqlite3 -header -column data/kinoplan.sqlite
--     sqlite> .read sql/queries.sql
-- Значения в условиях (даты, вместимость, id) приведены для проверки.
-- В веб-приложении (db/queries.py) они передаются параметрами ?.
-- В скобках указано, где запрос используется на сайте.


-- ---------- 1. Выборка списков ----------

-- 1.1. Список локаций по убыванию вместимости (/locations/)
SELECT id, name, address, capacity
FROM locations
ORDER BY capacity DESC, name;

-- 1.2. Сцены фильма по порядку (/films/<id>/)
SELECT number, description, crew_size
FROM scenes
WHERE film_id = 2
ORDER BY number;

-- 1.3. Вторая «страница» графика: 3 съёмки, пропустив первые 3
--      (LIMIT/OFFSET; ORDER BY обязателен для стабильного порядка)
SELECT id, shooting_date, location_id
FROM shootings
ORDER BY shooting_date, id
LIMIT 3 OFFSET 3;


-- ---------- 2. Фильтрация WHERE ----------

-- 2.1. Локации, вмещающие группу от 50 человек (/locations/?capacity=50)
SELECT id, name, address, capacity
FROM locations
WHERE capacity >= 50
ORDER BY capacity DESC, name;

-- 2.2. Фильм по идентификатору (/films/<id>/)
SELECT id, title, director
FROM films
WHERE id = 1;

-- 2.3. Активные съёмки в ноябре 2026 (BETWEEN, AND)
SELECT id, scene_id, location_id, shooting_date
FROM shootings
WHERE shooting_date BETWEEN '2026-11-01' AND '2026-11-30'
  AND is_cancelled = 0
ORDER BY shooting_date;

-- 2.4. Поиск сцен по фрагменту описания (LIKE, OR).
--      В SQLite LIKE не различает регистр только для латиницы,
--      поэтому для кириллицы проверяются оба варианта первой буквы
SELECT film_id, number, description
FROM scenes
WHERE description LIKE '%разговор%'
   OR description LIKE '%Разговор%';

-- 2.5. Локации без указанного адреса (проверка NULL — только IS NULL)
SELECT id, name
FROM locations
WHERE address IS NULL;

-- 2.6. Занята ли локация 1 на 2026-11-10: 1 — занята, 0 — свободна
--      (/locations/<id>/?date=...)
SELECT COUNT(*) AS busy_count
FROM shootings
WHERE location_id = 1
  AND shooting_date = '2026-11-10'
  AND is_cancelled = 0;


-- ---------- 3. Соединение таблиц JOIN ----------

-- 3.1. Полный график съёмок: съёмка → сцена → фильм, съёмка → локация
--      (/shootings/)
SELECT
    shootings.id,
    shootings.shooting_date,
    shootings.is_cancelled,
    films.title AS film_title,
    scenes.number AS scene_number,
    locations.name AS location_name
FROM shootings
JOIN scenes ON shootings.scene_id = scenes.id
JOIN films ON scenes.film_id = films.id
JOIN locations ON shootings.location_id = locations.id
ORDER BY shootings.shooting_date, shootings.id;

-- 3.2. Карточка одной съёмки со всеми связанными данными
--      (/shootings/<id>/)
SELECT
    shootings.id,
    shootings.shooting_date,
    shootings.is_cancelled,
    films.id AS film_id,
    films.title AS film_title,
    films.director AS film_director,
    scenes.number AS scene_number,
    scenes.description AS scene_description,
    scenes.crew_size,
    locations.id AS location_id,
    locations.name AS location_name,
    locations.address AS location_address,
    locations.capacity AS location_capacity
FROM shootings
JOIN scenes ON shootings.scene_id = scenes.id
JOIN films ON scenes.film_id = films.id
JOIN locations ON shootings.location_id = locations.id
WHERE shootings.id = 4;

-- 3.3. Съёмки одного фильма (/films/<id>/)
SELECT
    shootings.id,
    shootings.shooting_date,
    shootings.is_cancelled,
    films.title AS film_title,
    scenes.number AS scene_number,
    locations.name AS location_name
FROM shootings
JOIN scenes ON shootings.scene_id = scenes.id
JOIN films ON scenes.film_id = films.id
JOIN locations ON shootings.location_id = locations.id
WHERE films.id = 1
ORDER BY shootings.shooting_date;

-- 3.4. Съёмки на одной локации (/locations/<id>/)
SELECT
    shootings.id,
    shootings.shooting_date,
    shootings.is_cancelled,
    films.title AS film_title,
    scenes.number AS scene_number,
    locations.name AS location_name
FROM shootings
JOIN scenes ON shootings.scene_id = scenes.id
JOIN films ON scenes.film_id = films.id
JOIN locations ON shootings.location_id = locations.id
WHERE locations.id = 1
ORDER BY shootings.shooting_date;

-- 3.5. Три ближайшие активные съёмки начиная с 2026-10-26 (главная)
SELECT
    shootings.id,
    shootings.shooting_date,
    shootings.is_cancelled,
    films.title AS film_title,
    scenes.number AS scene_number,
    locations.name AS location_name
FROM shootings
JOIN scenes ON shootings.scene_id = scenes.id
JOIN films ON scenes.film_id = films.id
JOIN locations ON shootings.location_id = locations.id
WHERE shootings.is_cancelled = 0
  AND shootings.shooting_date >= '2026-10-26'
ORDER BY shootings.shooting_date, shootings.id
LIMIT 3;

-- 3.6. Фильмы, которые снимаются на локации 1 (DISTINCT убирает повторы)
SELECT DISTINCT films.title
FROM shootings
JOIN scenes ON shootings.scene_id = scenes.id
JOIN films ON scenes.film_id = films.id
WHERE shootings.location_id = 1
  AND shootings.is_cancelled = 0;

-- 3.7. Сцены без назначенной активной съёмки: LEFT JOIN + IS NULL
--      (/shootings/statistics/)
SELECT
    films.id AS film_id,
    films.title AS film_title,
    scenes.number AS scene_number,
    scenes.description,
    scenes.crew_size
FROM scenes
JOIN films ON scenes.film_id = films.id
LEFT JOIN shootings
    ON shootings.scene_id = scenes.id
   AND shootings.is_cancelled = 0
WHERE shootings.id IS NULL
ORDER BY films.title, scenes.number;

-- 3.8. Свободные на 2026-11-10 локации для группы от 40 человек:
--      подзапрос NOT IN исключает занятые (/locations/free/)
SELECT id, name, address, capacity
FROM locations
WHERE capacity >= 40
  AND id NOT IN (
      SELECT location_id
      FROM shootings
      WHERE shooting_date = '2026-11-10'
        AND is_cancelled = 0
  )
ORDER BY capacity, name;


-- ---------- 4. Агрегатные функции ----------

-- 4.1. Сводка для главной страницы: COUNT по трём таблицам
SELECT
    (SELECT COUNT(*) FROM films) AS films_count,
    (SELECT COUNT(*) FROM locations) AS locations_count,
    (SELECT COUNT(*) FROM shootings WHERE is_cancelled = 0) AS active_count;

-- 4.2. Итоги по съёмкам: всего, активных, отменённых, период
--      COUNT(выражение) не считает NULL, поэтому CASE без ELSE
--      считает только подходящие строки (/shootings/statistics/)
SELECT
    COUNT(*) AS total,
    COUNT(CASE WHEN is_cancelled = 0 THEN 1 END) AS active,
    COUNT(CASE WHEN is_cancelled = 1 THEN 1 END) AS cancelled,
    strftime('%d.%m.%Y', MIN(shooting_date)) AS first_date,
    strftime('%d.%m.%Y', MAX(shooting_date)) AS last_date
FROM shootings;

-- 4.3. Минимальная, максимальная и средняя вместимость локаций
SELECT
    MIN(capacity) AS min_capacity,
    MAX(capacity) AS max_capacity,
    ROUND(AVG(capacity), 1) AS avg_capacity,
    SUM(capacity) AS total_capacity
FROM locations;


-- ---------- 5. Группировка GROUP BY и HAVING ----------

-- 5.1. Фильмы с количеством сцен (/films/)
SELECT
    films.id,
    films.title,
    films.director,
    COUNT(scenes.id) AS scenes_count
FROM films
LEFT JOIN scenes ON scenes.film_id = films.id
GROUP BY films.id, films.title, films.director
ORDER BY films.title;

-- 5.2. Загрузка локаций: активные съёмки по каждой локации.
--      LEFT JOIN оставляет локации без съёмок (счётчик 0)
--      (/shootings/statistics/)
SELECT
    locations.id,
    locations.name,
    locations.capacity,
    COUNT(shootings.id) AS shootings_count,
    strftime('%d.%m.%Y', MIN(shootings.shooting_date)) AS first_date,
    strftime('%d.%m.%Y', MAX(shootings.shooting_date)) AS last_date
FROM locations
LEFT JOIN shootings
    ON shootings.location_id = locations.id
   AND shootings.is_cancelled = 0
GROUP BY locations.id, locations.name, locations.capacity
ORDER BY shootings_count DESC, locations.name;

-- 5.3. Сцены и размер групп по фильмам: COUNT, AVG, MAX, SUM
--      (/shootings/statistics/)
SELECT
    films.id,
    films.title,
    COUNT(scenes.id) AS scenes_count,
    ROUND(AVG(scenes.crew_size), 1) AS avg_crew,
    MAX(scenes.crew_size) AS max_crew,
    SUM(scenes.crew_size) AS total_crew
FROM films
LEFT JOIN scenes ON scenes.film_id = films.id
GROUP BY films.id, films.title
ORDER BY films.title;

-- 5.4. Активные съёмки по месяцам (/shootings/statistics/)
SELECT
    strftime('%m.%Y', shooting_date) AS month,
    COUNT(*) AS shootings_count
FROM shootings
WHERE is_cancelled = 0
GROUP BY strftime('%Y-%m', shooting_date)
ORDER BY strftime('%Y-%m', shooting_date);

-- 5.5. Загруженные локации: не меньше 2 активных съёмок.
--      WHERE отбирает строки до группировки, HAVING — группы после
--      (/shootings/statistics/?min=2)
SELECT
    locations.id,
    locations.name,
    COUNT(*) AS shootings_count
FROM shootings
JOIN locations ON shootings.location_id = locations.id
WHERE shootings.is_cancelled = 0
GROUP BY locations.id, locations.name
HAVING COUNT(*) >= 2
ORDER BY shootings_count DESC;
