-- Enable the pgcrypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    abbreviation VARCHAR(3) NOT NULL
);

-- Create players table
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    name VARCHAR(50) NOT NULL,
    position VARCHAR(2),
    comment TEXT
);

-- Create player history stats table
CREATE TABLE IF NOT EXISTS player_history_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    season VARCHAR(10),
    game_id INTEGER,
    player_id INTEGER REFERENCES players(id),
    start_position VARCHAR(10),
    minute FLOAT,
    fg_made INTEGER,
    fg_attempts INTEGER,
    fg_pct FLOAT,
    three_p_made INTEGER,
    three_p_attempts INTEGER,
    three_p_pct FLOAT,
    ft_made INTEGER,
    ft_attempts INTEGER,
    ft_pct FLOAT,
    offensive_rebounds INTEGER,
    defensive_rebounds INTEGER,
    rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,
    points INTEGER,
    plus_minus FLOAT,
    double_double BOOLEAN,
    triple_double BOOLEAN
);



-- TODO
-- Create games table
-- game_id
-- date
-- state
