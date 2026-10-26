-- ==========================================
-- КиноПлан: структура базы данных
-- ==========================================
-- Порядок создания важен: сначала таблицы, на которые ссылаются
-- внешние ключи (films, locations), затем зависимые (scenes, shootings).

-- Фильмы
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    director TEXT                       -- режиссёр может быть ещё не известен
);

-- Сцены фильма (в JSON вложены в фильм, в базе — отдельная таблица)
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY,
    film_id INTEGER NOT NULL,
    number INTEGER NOT NULL,            -- номер сцены внутри фильма
    description TEXT NOT NULL,
    crew_size INTEGER NOT NULL CHECK (crew_size > 0),
    FOREIGN KEY (film_id) REFERENCES films(id),
    UNIQUE (film_id, number)            -- в фильме нет двух сцен с одним номером
);

-- Локации
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,                       -- адрес допускается не указывать
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

-- Съёмки: какая сцена, где и когда снимается
CREATE TABLE IF NOT EXISTS shootings (
    id INTEGER PRIMARY KEY,
    scene_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    shooting_date TEXT NOT NULL,        -- дата в формате ГГГГ-ММ-ДД
    is_cancelled INTEGER NOT NULL DEFAULT 0 CHECK (is_cancelled IN (0, 1)),
    FOREIGN KEY (scene_id) REFERENCES scenes(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- На одной локации в один день — не больше одной активной съёмки.
-- Отменённые съёмки (is_cancelled = 1) индекс не учитывает.
CREATE UNIQUE INDEX IF NOT EXISTS idx_shootings_location_date
    ON shootings (location_id, shooting_date)
    WHERE is_cancelled = 0;
