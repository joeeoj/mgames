.mode csv
.header on

.open games.db

CREATE TABLE IF NOT EXISTS schedule (
    game_number INTEGER PRIMARY KEY,
    game_date DATE,
    day_of_week TEXT,
    game_time_local TEXT,
    is_home_game BOOLEAN,
    venue TEXT,
    series_number SMALLINT,
    day_night TEXT,
    home TEXT,
    away TEXT,
    home_game_number INTEGER
);

CREATE TABLE IF NOT EXISTS blocks (
    game_number INTEGER PRIMARY KEY,
    home_game_number INTEGER,
    blockset SMALLINT,
    FOREIGN KEY (game_number) REFERENCES schedule(game_number)
);

CREATE TABLE IF NOT EXISTS owners (
    home_game_number INTEGER PRIMARY KEY,
    owner TEXT,
    FOREIGN KEY (home_game_number) REFERENCES schedule(home_game_number)
);

CREATE VIEW IF NOT EXISTS home_games AS

SELECT DISTINCT
    s.game_number
    ,s.home_game_number
    ,s.game_date
    ,s.day_of_week
    ,s.game_time_local
    ,s.series_number
    ,s.day_night
    ,s.away
    ,b.blockset
    ,o.owner
FROM schedule s
JOIN blocks b
    ON s.game_number = b.game_number
LEFT JOIN owners o
    ON s.home_game_number = o.home_game_number
;

CREATE VIEW IF NOT EXISTS available_home_games AS
SELECT *
FROM home_games
WHERE
    game_date > CURRENT_DATE
    AND (owner IS NULL OR owner != 'M')
;

CREATE VIEW IF NOT EXISTS double_headers AS
SELECT
    game_date
    ,home
    ,away
    ,COUNT(*) as cnt
FROM schedule
GROUP BY 1
HAVING COUNT(*) > 1
;

.import --skip 1 ./data/schedule.csv schedule
.import --skip 1 ./data/blocks.csv blocks
.import --skip 1 ./data/owners.csv owners

PRAGMA foreign_keys=true;

VACUUM;
