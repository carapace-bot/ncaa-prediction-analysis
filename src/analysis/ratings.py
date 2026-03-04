import numpy as np
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RatingSystem:
    """Calculate team strength ratings from game results"""
    
    def __init__(self, k_factor=32):
        """
        Initialize ELO-style rating system
        k_factor: how much ratings change after each game
        """
        self.k_factor = k_factor
        self.ratings = {}
    
    def calculate_expected_score(self, rating1, rating2):
        """Calculate expected win probability for rating1 vs rating2"""
        return 1.0 / (1.0 + 10.0 ** ((rating2 - rating1) / 400.0))
    
    def update_rating(self, old_rating, expected, actual, k_factor=None):
        """Update rating based on game result"""
        if k_factor is None:
            k_factor = self.k_factor
        
        return old_rating + k_factor * (actual - expected)
    
    def rate_from_wins_losses(self, teams_data):
        """
        Simple rating based on win-loss record.
        teams_data: dict of {team_name: {'wins': w, 'losses': l}}
        
        Returns: dict of {team_name: strength_rating}
        """
        ratings = {}
        
        for team_name, data in teams_data.items():
            wins = data.get('wins', 0)
            losses = data.get('losses', 0)
            total = wins + losses
            
            if total > 0:
                win_pct = wins / total
                # Convert win% to 0-1 rating scale
                # Scale to roughly 0.3-0.7 for typical range
                rating = 0.3 + (win_pct * 0.4)
            else:
                rating = 0.5  # Default if no games
            
            ratings[team_name] = rating
        
        self.ratings = ratings
        return ratings
    
    def rate_with_strength_of_schedule(self, teams_data, opp_ratings=None):
        """
        Adjust ratings based on strength of schedule.
        teams_data: dict with win/loss records
        opp_ratings: dict of opponent ratings for SOS calculation
        """
        if opp_ratings is None:
            opp_ratings = {}
        
        base_ratings = self.rate_from_wins_losses(teams_data)
        adjusted_ratings = {}
        
        for team_name, base_rating in base_ratings.items():
            team_data = teams_data.get(team_name, {})
            opponents = team_data.get('opponents', [])
            
            if opponents:
                avg_opp_rating = np.mean([
                    opp_ratings.get(opp, 0.5) for opp in opponents
                ])
                # Adjust for SOS: teams beating strong opponents get boost
                adjustment = (avg_opp_rating - 0.5) * 0.1
                adjusted_rating = base_rating + adjustment
            else:
                adjusted_rating = base_rating
            
            # Clamp to reasonable range
            adjusted_rating = max(0.25, min(0.75, adjusted_rating))
            adjusted_ratings[team_name] = adjusted_rating
        
        self.ratings = adjusted_ratings
        return adjusted_ratings
    
    def elo_from_games(self, games_list, initial_rating=1500):
        """
        Calculate ELO ratings from game results.
        games_list: list of dicts with keys:
            - home_team, away_team
            - home_score, away_score
        """
        ratings = defaultdict(lambda: initial_rating)
        
        for game in games_list:
            home = game.get('home_team')
            away = game.get('away_team')
            home_score = game.get('home_score')
            away_score = game.get('away_score')
            
            if not all([home, away, home_score is not None, away_score is not None]):
                continue
            
            # Determine actual result (1 = home win, 0 = away win)
            actual = 1 if home_score > away_score else 0
            
            # Get current ratings
            home_rating = ratings[home]
            away_rating = ratings[away]
            
            # Calculate expected scores
            home_expected = self.calculate_expected_score(home_rating, away_rating)
            away_expected = 1 - home_expected
            
            # Update ratings with home court advantage factor
            home_advantage = 50  # Home court bonus
            ratings[home] = self.update_rating(
                home_rating,
                home_expected,
                actual,
                k_factor=self.k_factor
            ) + (home_advantage * actual)
            
            ratings[away] = self.update_rating(
                away_rating,
                away_expected,
                1 - actual,
                k_factor=self.k_factor
            )
        
        # Normalize to 0-1 scale
        normalized_ratings = {}
        min_rating = min(ratings.values())
        max_rating = max(ratings.values())
        rating_range = max_rating - min_rating
        
        for team, rating in ratings.items():
            if rating_range > 0:
                normalized = (rating - min_rating) / rating_range
                normalized = 0.25 + (normalized * 0.5)  # Scale to 0.25-0.75
            else:
                normalized = 0.5
            
            normalized_ratings[team] = normalized
        
        self.ratings = normalized_ratings
        return normalized_ratings
