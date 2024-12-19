import pandas as pd
import numpy as np
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime, timedelta
import logging
from tqdm import tqdm

from db import (
    connect_database,
    insert_game_stats_data,
    insert_player_data,
    insert_team_data,
)

from utils import fetch_stats_for_game

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

# Cache for storing already processed game IDs
processed_games = set()


# Query the scoreboard for yesterday's games
def get_game_ids():
    yesterday = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")
    scoreboard = scoreboardv2.ScoreboardV2(game_date=yesterday)
    games = scoreboard.game_header.get_data_frame()

    # Extract game IDs
    game_ids = games["GAME_ID"].tolist()
    return game_ids


def main():
    logging.info("Starting player daily stats cronjob")
    try:
        db = connect_database()
        game_ids = get_game_ids()
        season = "2024-2025"
        # Process games with progress bar
        for game_id in tqdm(game_ids, desc=f"Processing {season} games"):
            if game_id in processed_games:
                return None, None, None

            teams_df, players_df, stats_df = fetch_stats_for_game(game_id, season)
            if not teams_df.empty:
                insert_team_data(db, teams_df)

            # Insert players data
            if not players_df.empty:
                insert_player_data(db, players_df)

            # Insert game stats data
            if not stats_df.empty:
                insert_game_stats_data(db, stats_df)

            processed_games.add(game_id)

        else:
            logging.warning("No valid game data found")

    except Exception as e:
        logging.error(f"Database error: {str(e)}")


if __name__ == "__main__":
    main()
