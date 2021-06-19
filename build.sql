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

CREATE VIEW IF NOT EXISTS upcoming_home_games AS

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
FROM schedule s
JOIN blocks b
    ON s.game_number = b.game_number
WHERE
    s.game_date >= CURRENT_DATE
;

.headers on
.mode csv

.import ./data/schedule.csv schedule
.import ./data/blocks.csv blocks

PRAGMA foreign_keys=true;

VACUUM;
