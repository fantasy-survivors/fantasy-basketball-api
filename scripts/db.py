# Move column mapping to a constant at module level
import os
import logging
import psycopg2
from psycopg2.extensions import connection
from pandas import DataFrame


def connect_database():
    """Create a database connection."""
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    dbname = os.getenv("POSTGRES_DB")

    print(host, port, user, password, dbname)
    return psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname=dbname
    )


def create_tables():
    """Create tables in the database."""
    conn = connect_database()
    cursor = conn.cursor()

    logging.info("Connected to database")

    # Create tables if they don't exist
    tables = [
        """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            abbreviation VARCHAR(3) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id),
            name VARCHAR(50) NOT NULL,
            position VARCHAR(2) NOT NULL,
            comment TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS player_history_stats (
            id SERIAL PRIMARY KEY,
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
        """,
    ]

    for table in tables:
        cursor.execute(table)

    conn.commit()
    logging.info("Database tables ready")


def insert_team_data(db: connection, teams_df: DataFrame):
    """Insert team data into the database."""
    cursor = db.cursor()

    for _, team in teams_df.iterrows():
        team_id = team["TEAM_ID"]
        cursor.execute("SELECT * FROM teams WHERE id = %s", (team_id,))
        if cursor.fetchone():
            continue
        cursor.execute(
            """
            INSERT INTO teams (id, abbreviation) 
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (team["TEAM_ID"], team["TEAM_ABBREVIATION"]),
        )
    db.commit()
    print("Insert {} data to teams".format(len(teams_df)))


def insert_player_data(db: connection, players_df: DataFrame):
    """Insert player data into the database."""
    cursor = db.cursor()
    for _, player in players_df.iterrows():
        player_id = player["PLAYER_ID"]
        cursor.execute("SELECT * FROM players WHERE id = %s", (player_id,))
        if cursor.fetchone():
            continue
        cursor.execute(
            """
            INSERT INTO players (id, team_id, name, position, comment)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                player["PLAYER_ID"],
                player["TEAM_ID"],
                player["PLAYER_NAME"],
                player["START_POSITION"],
                player["COMMENT"],
            ),
        )
    db.commit()
    print("Insert {} data to players".format(len(players_df)))


def insert_game_stats_data(db: connection, stats_df: DataFrame):
    """Insert game stats data into the database."""
    cursor = db.cursor()
    for _, stat in stats_df.iterrows():
        game_id, player_id = stat["GAME_ID"], stat["PLAYER_ID"]
        cursor.execute(
            "SELECT * FROM player_history_stats WHERE game_id = %s AND player_id = %s",
            (
                game_id,
                player_id,
            ),
        )
        data = cursor.fetchone()
        if data:
            continue
        cursor.execute(
            """
            INSERT INTO player_history_stats (
                season, game_id, player_id, start_position, minute, fg_made, fg_attempts,
                fg_pct, three_p_made, three_p_attempts, three_p_pct,
                ft_made, ft_attempts, ft_pct, offensive_rebounds,
                defensive_rebounds, rebounds, assists, steals, blocks,
                turnovers, personal_fouls, points, plus_minus,
                double_double, triple_double
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                stat["SEASON"],
                stat["GAME_ID"],
                stat["PLAYER_ID"],
                stat["START_POSITION"],
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
                stat["OREB"],
                stat["DREB"],
                stat["REB"],
                stat["AST"],
                stat["STL"],
                stat["BLK"],
                stat["TO"],
                stat["PF"],
                stat["PTS"],
                stat["PLUS_MINUS"],
                stat["DOUBLE_DOUBLE"],
                stat["TRIPLE_DOUBLE"],
            ),
        )

    db.commit()
    print("Insert {} data to history data".format(len(stats_df)))
