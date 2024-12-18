import logging
import os
import time
from typing import Tuple, Optional

import pandas as pd
from nba_api.stats.endpoints import LeagueGameLog, BoxScoreTraditionalV2
from tqdm import tqdm

from utils import (
    COLUMN_MAPPING,
    create_tables,
    connect_database,
    insert_game_stats_data,
    insert_player_data,
    insert_team_data,
)

# Configure logging with more concise format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

# Cache for storing already processed game IDs
processed_games = set()


def calculate_double_triple_double(row: pd.Series) -> Tuple[bool, bool]:
    """Calculate if player achieved double-double or triple-double."""
    stats = [row["PTS"], row["REB"], row["AST"], row["BLK"], row["STL"]]
    doubles = sum(x >= 10 for x in stats)
    return doubles >= 2, doubles >= 3


def fetch_stats_for_game(
    game_id: str, season: str, timeout: int = 30
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Fetch and process stats for a single game."""
    if game_id in processed_games:
        return None, None, None

    try:
        # Rate limiting
        time.sleep(1)

        # Fetch box score data
        box_score = BoxScoreTraditionalV2(game_id=game_id, timeout=timeout)
        result = box_score.get_dict()["resultSets"][0]
        game_df = pd.DataFrame(result["rowSet"], columns=result["headers"])

        if game_df.empty:
            return None, None, None

        # Add metadata columns
        game_df["SEASON"] = season
        game_df[["GAME_ID", "TEAM_ID", "PLAYER_ID"]] = game_df[
            ["GAME_ID", "TEAM_ID", "PLAYER_ID"]
        ].apply(pd.to_numeric)

        # Process minutes played
        game_df["MIN"] = pd.to_numeric(
            game_df["MIN"].str.split(":").str[0], errors="coerce"
        )

        # Calculate achievements
        game_df[["DOUBLE_DOUBLE", "TRIPLE_DOUBLE"]] = pd.DataFrame(
            [calculate_double_triple_double(row) for _, row in game_df.iterrows()],
            index=game_df.index,
        )

        # Split into separate dataframes
        team_cols = ["TEAM_ID", "TEAM_ABBREVIATION"]
        player_cols = ["PLAYER_ID", "PLAYER_NAME", "START_POSITION", "COMMENT"]
        game_cols = [
            col for col in COLUMN_MAPPING.keys() if col not in team_cols + player_cols
        ]

        team_df = game_df[team_cols].drop_duplicates()
        player_df = game_df[player_cols].drop_duplicates()
        game_stats_df = game_df[game_cols]

        # Rename columns
        team_df.rename(columns=COLUMN_MAPPING)
        player_df.rename(columns=COLUMN_MAPPING)
        game_stats_df.rename(columns=COLUMN_MAPPING)

        processed_games.add(game_id)

        return team_df, player_df, game_stats_df

    except Exception as e:
        logging.error(f"Error fetching game {game_id}: {str(e)}")
        return None, None, None


def main():
    """Main entry point."""
    try:
        create_tables()
        db = connect_database()

        season = "2023-24"
        game_log = LeagueGameLog(season=season)
        games = game_log.get_data_frames()[0]
        game_ids = games["GAME_ID"].unique()

        # Process games with progress bar
        for game_id in tqdm(game_ids, desc=f"Processing {season} games"):
            teams_df, players_df, stats_df = fetch_stats_for_game(game_id, season)

            if not teams_df.empty():
                insert_team_data(db, teams_df)

            # Insert players data
            if not players_df.empty():
                insert_player_data(db, players_df)

            # Insert game stats data
            if not stats_df.empty():
                insert_game_stats_data(db, stats_df)

        else:
            logging.warning("No valid game data found")

    except Exception as e:
        logging.error(f"Database error: {str(e)}")


if __name__ == "__main__":
    main()
