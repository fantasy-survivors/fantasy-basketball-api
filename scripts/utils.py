# Move column mapping to a constant at module level
import os
import logging
import psycopg2

COLUMN_MAPPING = {
    "SEASON": "season",
    "GAME_ID": "game_id",
    "TEAM_ID": "team_id",
    "TEAM_ABBREVIATION": "team_abbreviation",
    "PLAYER_ID": "player_id",
    "PLAYER_NAME": "player_name",
    "START_POSITION": "start_position",
    "COMMENT": "comment",
    "MIN": "minute",
    "FGM": "fg_made",
    "FGA": "fg_attempts",
    "FG_PCT": "fg_pct",
    "FG3M": "three_p_made",
    "FG3A": "three_p_attempts",
    "FG3_PCT": "three_p_pct",
    "FTM": "ft_made",
    "FTA": "ft_attempts",
    "FT_PCT": "ft_pct",
    "OREB": "offensive_rebounds",
    "DREB": "defensive_rebounds",
    "REB": "rebounds",
    "AST": "assists",
    "STL": "steals",
    "BLK": "blocks",
    "TO": "turnovers",
    "PF": "personal_fouls",
    "PTS": "points",
    "PLUS_MINUS": "plus_minus",
    "DOUBLE_DOUBLE": "double_double",
    "TRIPLE_DOUBLE": "triple_double",
}


def db_connection():
    """Create a database connection."""
    host = os.getenv("DOCKER_HOST")
    user = os.getenv("DOCKER_USER")
    password = os.getenv("DOCKER_PASSWORD")
    dbname = os.getenv("DOCKER_DB")

    return psycopg2.connect(
        host=host, port=5432, user=user, password=password, dbname=dbname
    )


def create_tables():
    """Create tables in the database."""
    db = db_connection()

    with db:
        with db.cursor() as cursor:
            logging.info("Connected to database")

            # Create tables if they don't exist
            tables = [
                """
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    team_id INTEGER REFERENCES teams(id),
                    name VARCHAR(100),
                    starting_position VARCHAR(10),
                    comment TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS player_history_stats (
                    id SERIAL PRIMARY KEY,
                    season VARCHAR(10),
                    game_id INTEGER,
                    player_id INTEGER REFERENCES players(id),
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
                """,
            ]

            for table in tables:
                cursor.execute(table)

            db.commit()
            logging.info("Database tables ready")


def insert_team_data(teams_df):
    """Insert team data into the database."""
    db = db_connection()
    with db:
        with db.cursor() as cursor:
            for _, team in teams_df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO teams (id, name) 
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (team["TEAM_ID"], team["TEAM_ABBREVIATION"]),
                )
            db.commit()
        db.close()


def insert_player_data(players_df):
    """Insert player data into the database."""
    db = db_connection()
    with db:
        with db.cursor() as cursor:
            for _, player in players_df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO players (id, name, starting_position, comment)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        player["PLAYER_ID"],
                        player["PLAYER_NAME"],
                        player["START_POSITION"],
                        player["COMMENT"],
                    ),
                )
            db.commit()
        db.close()


def insert_game_stats_data(stats_df):
    """Insert game stats data into the database."""
    db = db_connection()
    with db:
        with db.cursor() as cursor:
            for _, stat in stats_df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO player_history_stats (
                    season, game_id, player_id, minute, fg_made, fg_attempts,
                    fg_pct, three_p_made, three_p_attempts, three_p_pct,
                    ft_made, ft_attempts, ft_pct, offensive_rebounds,
                    defensive_rebounds, rebounds, assists, steals, blocks,
                    turnovers, personal_fouls, points, plus_minus,
                    double_double, triple_double
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        stat["SEASON"],
                        stat["GAME_ID"],
                        stat["PLAYER_ID"],
                        stat["MIN"],
                        stat["FGM"],
                        stat["FGA"],
                        stat["FG_PCT"],
                        stat["FG3M"],
                        stat["FG3A"],
                        stat["FG3_PCT"],
                        stat["FTM"],
                        stat["FTA"],
                        stat["FT_PCT"],
                        stat["TO"],
                        stat["PF"],
                        stat["PTS"],
                        stat["PLUS_MINUS"],
                        stat["DOUBLE_DOUBLE"],
                        stat["TRIPLE_DOUBLE"],
                    ),
                )
            db.commit()
        db.close()
