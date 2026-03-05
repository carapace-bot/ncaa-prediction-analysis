import random
import numpy as np
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TournamentSimulator:
    """Monte Carlo simulation of NCAA tournament outcomes"""
    
    def __init__(self, team_ratings):
        """
        Initialize with team ratings (0-1 scale, higher = better)
        team_ratings: dict of {team_name: strength_rating}
        """
        self.team_ratings = team_ratings
        self.results = defaultdict(lambda: defaultdict(int))
    
    def calculate_win_probability(self, team1_rating, team2_rating):
        """
        Calculate P(team1 beats team2) using logistic model.
        Ratings are on 0-1 scale (not ELO 1500 scale).
        """
        rating_diff = team1_rating - team2_rating
        # For 0-1 scale ratings, use a steeper curve
        # A 0.1 rating difference ~ 65% win probability
        prob = 1.0 / (1.0 + 10.0 ** (-rating_diff * 8.0))
        return prob
    
    def simulate_game(self, team1, team2):
        """
        Simulate a single game between two teams.
        Returns winner name.
        """
        rating1 = self.team_ratings.get(team1, 0.5)
        rating2 = self.team_ratings.get(team2, 0.5)
        
        win_prob = self.calculate_win_probability(rating1, rating2)
        
        if random.random() < win_prob:
            return team1
        else:
            return team2
    
    def simulate_tournament(self, teams):
        """
        Simulate a single tournament run.
        teams: flat list of teams in bracket order (matchups are adjacent pairs).
        Plays through rounds until one champion remains.
        Returns final champion.
        """
        current_round = list(teams)
        
        while len(current_round) > 1:
            next_round = []
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    winner = self.simulate_game(current_round[i], current_round[i + 1])
                    next_round.append(winner)
                else:
                    # Odd team gets a bye
                    next_round.append(current_round[i])
            current_round = next_round
        
        return current_round[0] if current_round else None
    
    def run_simulations(self, teams, num_simulations=10000):
        """
        Run multiple tournament simulations and track outcomes.
        
        teams: flat list of teams in bracket order
        num_simulations: number of times to run tournament
        
        Returns: dict with probability of each team winning championship
        """
        champion_counts = defaultdict(int)
        
        logger.info(f"Running {num_simulations} tournament simulations with {len(teams)} teams...")
        
        for i in range(num_simulations):
            if (i + 1) % 2000 == 0:
                logger.info(f"  Completed {i + 1}/{num_simulations}")
            
            champion = self.simulate_tournament(teams)
            if champion:
                champion_counts[champion] += 1
        
        # Convert counts to probabilities
        championship_odds = {}
        for team, count in champion_counts.items():
            championship_odds[team] = count / num_simulations
        
        # Sort by probability descending
        sorted_odds = sorted(championship_odds.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"Simulation complete. Top 10 favorites:")
        for team, prob in sorted_odds[:10]:
            logger.info(f"  {team}: {prob:.2%}")
        
        return dict(sorted_odds)
    
    def calculate_final_four_odds(self, teams, num_simulations=10000):
        """Calculate probability each team reaches Final Four (last 4 remaining)"""
        final_four_counts = defaultdict(int)
        
        for i in range(num_simulations):
            current_round = list(teams)
            
            # Simulate until we have 4 or fewer teams
            while len(current_round) > 4:
                next_round = []
                for j in range(0, len(current_round), 2):
                    if j + 1 < len(current_round):
                        winner = self.simulate_game(current_round[j], current_round[j + 1])
                        next_round.append(winner)
                    else:
                        next_round.append(current_round[j])
                current_round = next_round
            
            for team in current_round:
                final_four_counts[team] += 1
        
        final_four_odds = {}
        for team, count in final_four_counts.items():
            final_four_odds[team] = count / num_simulations
        
        return dict(sorted(final_four_odds.items(), key=lambda x: x[1], reverse=True))
