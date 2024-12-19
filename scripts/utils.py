from typing import Tuple, Optional
import pandas as pd
from nba_api.stats.endpoints import BoxScoreTraditionalV2
import time
import logging

# Configure logging with more concise format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

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


def calculate_double_triple_double(row: pd.Series) -> Tuple[bool, bool]:
    """Calculate if player achieved double-double or triple-double."""
    stats = [row["PTS"], row["REB"], row["AST"], row["BLK"], row["STL"]]
    doubles = sum(x >= 10 for x in stats)
    return doubles >= 2, doubles >= 3


def fetch_stats_for_game(
    game_id: str, season: str, timeout: int = 30
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Fetch and process stats for a single game."""
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

        # Fill NaN values with 0
        game_df = game_df.fillna(0)

        # Calculate achievements
        game_df[["DOUBLE_DOUBLE", "TRIPLE_DOUBLE"]] = pd.DataFrame(
            [calculate_double_triple_double(row) for _, row in game_df.iterrows()],
            index=game_df.index,
        )

        # Split into separate dataframes
        team_cols = ["TEAM_ID", "TEAM_ABBREVIATION"]
        player_cols = [
            "PLAYER_ID",
            "TEAM_ID",
            "PLAYER_NAME",
            "START_POSITION",
            "COMMENT",
        ]
        game_cols = [col for col in COLUMN_MAPPING.keys()]

        team_df = game_df[team_cols].drop_duplicates()
        player_df = game_df[player_cols].drop_duplicates()
        game_stats_df = game_df[game_cols]

        # Rename columns
        team_df.rename(columns=COLUMN_MAPPING)
        player_df.rename(columns=COLUMN_MAPPING)
        game_stats_df.rename(columns=COLUMN_MAPPING)

        return team_df, player_df, game_stats_df

    except Exception as e:
        logging.error(f"Error fetching game {game_id}: {str(e)}")
        return None, None, None


# # Get **all** the games so we can filter to an individual GAME_ID
# result = leaguegamefinder.LeagueGameFinder()
# all_games = result.get_data_frames()[0]
# # Find the game_id we want
# full_game = all_games[all_games.GAME_ID == game_id]
# full_game
