#!/usr/bin/env python3
"""
NCAA Tournament Market Analysis Script
Fetches team data, calculates ratings, simulates tournament, compares to Polymarket
"""

import sys
import json
import os
from datetime import datetime

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.scraping.espn_scraper import ESPNScraper
from src.scraping.net_scraper import NETScraper
from src.analysis.ratings import RatingSystem
from src.analysis.simulator import TournamentSimulator
from src.markets.polymarket_analyzer import PolymarketAnalyzer

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("NCAA Tournament Prediction Market Analysis")
    logger.info("=" * 60)
    
    # Step 1: Fetch team data
    logger.info("\n[1] Fetching team data from ESPN...")
    espn = ESPNScraper()
    rankings = espn.get_rankings()
    schedule = espn.get_schedule()
    
    logger.info(f"  Retrieved {len(rankings)} ranked teams")
    logger.info(f"  Retrieved {len(schedule)} games from schedule")
    
    # Step 2: Calculate team ratings
    logger.info("\n[2] Calculating team strength ratings...")
    rating_system = RatingSystem()
    
    # Build win-loss records from schedule
    teams_data = {}
    for game in schedule:
        if game['home_score'] is not None and game['away_score'] is not None:
            home = game['home_team']
            away = game['away_team']
            
            if not home or not away:
                continue
            
            home_name = home['name'] if isinstance(home, dict) else home
            away_name = away['name'] if isinstance(away, dict) else away
            
            if home_name not in teams_data:
                teams_data[home_name] = {'wins': 0, 'losses': 0}
            if away_name not in teams_data:
                teams_data[away_name] = {'wins': 0, 'losses': 0}
            
            # Update based on game result
            if game['home_score'] > game['away_score']:
                teams_data[home_name]['wins'] += 1
                teams_data[away_name]['losses'] += 1
            else:
                teams_data[home_name]['losses'] += 1
                teams_data[away_name]['wins'] += 1
    
    # Calculate ratings
    ratings = rating_system.rate_from_wins_losses(teams_data)
    
    logger.info(f"  Calculated ratings for {len(ratings)} teams")
    logger.info(f"  Top 5 teams by rating:")
    for team, rating in sorted(ratings.items(), key=lambda x: x[1], reverse=True)[:5]:
        logger.info(f"    {team}: {rating:.4f}")
    
    # Step 3: Search for tournament markets
    logger.info("\n[3] Searching for NCAA tournament markets on Polymarket...")
    analyzer = PolymarketAnalyzer()
    markets = analyzer.search_markets("NCAA tournament")
    
    if markets:
        logger.info(f"  Found {len(markets)} NCAA markets")
        for market in markets[:5]:
            market_title = market.get('title', market.get('question'))
            logger.info(f"    - {market_title}")
    else:
        logger.info("  No markets found. Polymarket API may be unavailable.")
    
    # Step 4: Build tournament bracket (using top 68 teams by rating)
    logger.info("\n[4] Building tournament bracket from rated teams...")
    top_teams = sorted(
        [(team, rating) for team, rating in ratings.items()],
        key=lambda x: x[1],
        reverse=True
    )[:68]
    
    top_team_names = [team for team, _ in top_teams]
    logger.info(f"  Selected {len(top_team_names)} teams for simulation")
    
    # For demo: create simplified bracket (16 teams)
    demo_bracket = [top_team_names[:16]]  # Sweet 16
    demo_bracket.append(demo_bracket[0][:8])  # Elite 8
    demo_bracket.append(demo_bracket[1][:4])  # Final 4
    demo_bracket.append(demo_bracket[2][:2])  # Championship
    
    # Step 5: Simulate tournament
    logger.info("\n[5] Running tournament simulations (10,000 runs)...")
    simulator = TournamentSimulator({
        team: ratings.get(team, 0.5) for team in top_team_names
    })
    
    championship_odds = simulator.run_simulations(demo_bracket, num_simulations=10000)
    
    logger.info(f"\n  Championship Odds (Model):")
    sorted_odds = sorted(championship_odds.items(), key=lambda x: x[1], reverse=True)
    for team, prob in sorted_odds[:10]:
        logger.info(f"    {team}: {prob:.2%}")
    
    # Step 6: Compare to market (if markets found)
    logger.info("\n[6] Comparing model vs market odds...")
    
    if markets:
        mispricings = []
        for market in markets[:3]:  # Check first 3 markets
            market_id = market.get('id')
            if not market_id:
                continue
            
            details = analyzer.get_market_details(market_id)
            odds = analyzer.extract_implied_odds(details)
            
            if odds:
                logger.info(f"\n  Market: {market.get('title')}")
                logger.info(f"  Current odds: {odds}")
                
                # Convert odds to probabilities
                market_odds = {k: float(v) for k, v in odds.items() if isinstance(v, (int, float))}
                
                if market_odds:
                    # Find mismatches
                    for outcome, market_prob in market_odds.items():
                        for team, model_prob in sorted(championship_odds.items(), key=lambda x: x[1], reverse=True):
                            if team.lower() in outcome.lower() or outcome.lower() in team.lower():
                                edge = model_prob - market_prob
                                if abs(edge) > 0.05:
                                    logger.info(f"    {team}:")
                                    logger.info(f"      Model: {model_prob:.2%}")
                                    logger.info(f"      Market: {market_prob:.2%}")
                                    logger.info(f"      Edge: {edge:+.2%}")
    else:
        logger.info("  No markets available for comparison")
    
    # Step 7: Save results
    logger.info("\n[7] Saving results...")
    sorted_odds = sorted(championship_odds.items(), key=lambda x: x[1], reverse=True)
    output = {
        'timestamp': datetime.now().isoformat(),
        'team_ratings': {team: float(rating) for team, rating in ratings.items()},
        'championship_odds': championship_odds,
        'top_10_favorites': [
            {'team': team, 'probability': prob}
            for team, prob in sorted_odds[:10]
        ]
    }
    
    output_path = os.path.join(project_root, 'output', 'latest_analysis.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"  Results saved to {output_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Analysis complete!")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
