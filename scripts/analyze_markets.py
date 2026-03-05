#!/usr/bin/env python3
"""
NCAA Tournament Market Analysis Script
Fetches team data, calculates ratings, simulates tournament, compares to Polymarket
"""

import sys
import json
import os
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.scraping.espn_scraper import ESPNScraper
from src.analysis.ratings import RatingSystem
from src.analysis.simulator import TournamentSimulator
from src.markets.polymarket_analyzer import PolymarketAnalyzer

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_bracket(team_names, team_ratings):
    """
    Build a 64-team bracket in proper seed order for simulation.
    Teams are ordered by rating. Bracket matchups follow standard NCAA format:
    1 vs 16, 8 vs 9, 5 vs 12, 4 vs 13, 6 vs 11, 3 vs 14, 7 vs 10, 2 vs 15
    across 4 regions.
    
    If fewer than 64 teams, pad with generic low-rated teams.
    """
    # Sort by rating descending to assign seeds
    sorted_teams = sorted(team_names, key=lambda t: team_ratings.get(t, 0.0), reverse=True)
    
    # Pad to 64 if needed
    while len(sorted_teams) < 64:
        filler = f"Auto-Bid-{len(sorted_teams)+1}"
        sorted_teams.append(filler)
        team_ratings[filler] = 0.35  # Low rating for filler teams
    
    # Assign seeds 1-16 across 4 regions (S-curve assignment)
    # Seeds[0] = all #1 seeds, Seeds[1] = all #2 seeds, etc.
    seeds = [[] for _ in range(16)]
    for i, team in enumerate(sorted_teams[:64]):
        seed_num = i // 4  # 0-15
        seeds[seed_num].append(team)
    
    # Standard NCAA bracket matchup order within each region:
    # 1v16, 8v9, 5v12, 4v13, 6v11, 3v14, 7v10, 2v15
    matchup_order = [0, 15, 7, 8, 4, 11, 3, 12, 5, 10, 2, 13, 6, 9, 1, 14]
    
    bracket = []
    for region in range(4):
        for seed_idx in matchup_order:
            if region < len(seeds[seed_idx]):
                bracket.append(seeds[seed_idx][region])
            else:
                bracket.append(f"Filler-{seed_idx}-{region}")
    
    return bracket


def main():
    logger.info("=" * 60)
    logger.info("NCAA Tournament Prediction Market Analysis")
    logger.info(f"Run time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Step 1: Fetch team data from ESPN
    logger.info("\n[1] Fetching team data from ESPN (rankings + records)...")
    espn = ESPNScraper()
    
    all_team_data = espn.get_all_ranked_team_data()
    
    if not all_team_data:
        logger.error("Failed to fetch any team data. Aborting.")
        sys.exit(1)
    
    logger.info(f"  Retrieved data for {len(all_team_data)} teams")
    
    # Step 2: Build team records from fetched data
    logger.info("\n[2] Building team records...")
    teams_data = {}
    team_id_to_short_name = {}
    
    for team_id, data in all_team_data.items():
        short_name = data.get('short_name', data.get('name', f'Team-{team_id}'))
        record = data.get('record', {})
        
        team_id_to_short_name[team_id] = short_name
        
        wins = record.get('wins', 0)
        losses = record.get('losses', 0)
        
        if wins + losses == 0:
            # Try to parse from record_summary like "28-2"
            summary = record.get('record_summary', '')
            if '-' in summary:
                parts = summary.split('-')
                try:
                    wins = int(parts[0])
                    losses = int(parts[1])
                except ValueError:
                    pass
        
        teams_data[short_name] = {
            'wins': wins,
            'losses': losses,
            'rank': data.get('rank'),
            'points_for': record.get('avg_points_for', 0),
            'points_against': record.get('avg_points_against', 0),
            'differential': record.get('point_differential', 0),
        }
        
        logger.info(f"  {short_name}: {wins}-{losses} (AP #{data.get('rank', 'NR')})")
    
    # Step 3: Calculate ratings
    logger.info("\n[3] Calculating team strength ratings...")
    rating_system = RatingSystem()
    
    # Method 1: Win-loss based ratings
    wl_ratings = rating_system.rate_from_wins_losses(teams_data)
    
    # Method 2: ELO from actual games
    logger.info("  Collecting all game results for ELO calculation...")
    all_games = []
    seen_game_ids = set()
    
    for team_id, data in all_team_data.items():
        schedule = data.get('schedule', [])
        for game in schedule:
            game_id = game.get('id')
            if game_id and game_id not in seen_game_ids:
                seen_game_ids.add(game_id)
                
                home = game.get('home_team', {})
                away = game.get('away_team', {})
                
                if home and away:
                    all_games.append({
                        'home_team': home.get('short_name', home.get('name', '')),
                        'away_team': away.get('short_name', away.get('name', '')),
                        'home_score': game.get('home_score'),
                        'away_score': game.get('away_score'),
                    })
    
    logger.info(f"  Collected {len(all_games)} unique games")
    
    elo_ratings = {}
    if all_games:
        elo_ratings = rating_system.elo_from_games(all_games)
    
    # Blend ratings: 60% ELO + 40% win-loss (if ELO available)
    blended_ratings = {}
    all_team_names = set(list(wl_ratings.keys()) + list(elo_ratings.keys()))
    
    for team in all_team_names:
        wl = wl_ratings.get(team, 0.5)
        elo = elo_ratings.get(team, 0.5)
        
        if team in elo_ratings and team in wl_ratings:
            blended_ratings[team] = 0.6 * elo + 0.4 * wl
        elif team in elo_ratings:
            blended_ratings[team] = elo
        else:
            blended_ratings[team] = wl
    
    logger.info(f"  Calculated blended ratings for {len(blended_ratings)} teams")
    logger.info("  Top 10 by blended rating:")
    for team, rating in sorted(blended_ratings.items(), key=lambda x: x[1], reverse=True)[:10]:
        td = teams_data.get(team, {})
        logger.info(f"    {team}: {rating:.4f} ({td.get('wins',0)}-{td.get('losses',0)}, AP #{td.get('rank', 'NR')})")
    
    # Step 4: Build tournament bracket
    logger.info("\n[4] Building 64-team tournament bracket...")
    ranked_teams = [t for t in blended_ratings.keys() if t in teams_data]
    bracket = build_bracket(ranked_teams, blended_ratings)
    logger.info(f"  Bracket has {len(bracket)} teams")
    
    # Step 5: Run simulations
    logger.info("\n[5] Running tournament simulations (10,000 runs)...")
    simulator = TournamentSimulator(blended_ratings)
    championship_odds = simulator.run_simulations(bracket, num_simulations=10000)
    
    # Also get Final Four odds
    logger.info("  Running Final Four probability simulations...")
    ff_odds = simulator.calculate_final_four_odds(bracket, num_simulations=10000)
    
    # Step 6: Search Polymarket for NCAA markets
    logger.info("\n[6] Searching Polymarket for NCAA tournament markets...")
    poly = PolymarketAnalyzer()
    markets = poly.search_markets("NCAA tournament")
    
    if markets:
        logger.info(f"  Found {len(markets)} NCAA markets")
    else:
        logger.info("  No markets found via direct API. Using tool-based market data if available.")
    
    # Step 7: Compare model to known market prices
    logger.info("\n[7] Model vs Market comparison:")
    logger.info("-" * 60)
    
    # Format output table
    sorted_model = sorted(championship_odds.items(), key=lambda x: x[1], reverse=True)
    
    # Only show teams with >0.5% championship probability
    significant_teams = [(t, p) for t, p in sorted_model if p >= 0.005]
    
    logger.info(f"{'Team':<25} {'Model %':>10} {'W-L':>8} {'AP Rank':>8}")
    logger.info("-" * 55)
    for team, prob in significant_teams[:25]:
        td = teams_data.get(team, {})
        rank_str = f"#{td.get('rank')}" if td.get('rank') else 'NR'
        wl_str = f"{td.get('wins', '?')}-{td.get('losses', '?')}"
        logger.info(f"  {team:<23} {prob:>9.2%} {wl_str:>8} {rank_str:>8}")
    
    # Step 8: Save results
    logger.info("\n[8] Saving results...")
    output = {
        'timestamp': datetime.now().isoformat(),
        'team_count': len(blended_ratings),
        'games_analyzed': len(all_games),
        'simulations': 10000,
        'team_ratings': {team: float(rating) for team, rating in blended_ratings.items()},
        'championship_odds': championship_odds,
        'final_four_odds': ff_odds,
        'top_25_favorites': [
            {
                'team': team,
                'championship_probability': prob,
                'final_four_probability': ff_odds.get(team, 0),
                'wins': teams_data.get(team, {}).get('wins', 0),
                'losses': teams_data.get(team, {}).get('losses', 0),
                'ap_rank': teams_data.get(team, {}).get('rank'),
                'rating': blended_ratings.get(team, 0),
            }
            for team, prob in sorted_model[:25]
        ],
        'team_records': {
            team: {
                'wins': td.get('wins', 0),
                'losses': td.get('losses', 0),
                'rank': td.get('rank'),
                'points_for': td.get('points_for', 0),
                'points_against': td.get('points_against', 0),
            }
            for team, td in teams_data.items()
        }
    }
    
    output_dir = os.path.join(project_root, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'latest_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Also save timestamped copy
    ts_path = os.path.join(output_dir, f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(ts_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"  Results saved to {output_path}")
    logger.info(f"  Timestamped copy: {ts_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Analysis complete!")
    logger.info("=" * 60)
    
    return output


if __name__ == '__main__':
    main()
