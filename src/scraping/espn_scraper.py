import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ESPNScraper:
    """Scrape NCAA basketball data from ESPN"""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball"
    
    def get_rankings(self):
        """Fetch current power rankings"""
        try:
            url = f"{self.BASE_URL}/rankings"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            rankings = {}
            if 'rankings' in data:
                for rank_group in data['rankings']:
                    for team in rank_group.get('entries', []):
                        team_id = team.get('id')
                        team_name = team.get('displayName', team.get('name'))
                        rank = team.get('displayRank')
                        if team_id and team_name:
                            rankings[team_id] = {
                                'name': team_name,
                                'rank': rank,
                                'confidence': team.get('confidence')
                            }
            
            logger.info(f"Fetched {len(rankings)} team rankings from ESPN")
            return rankings
        except Exception as e:
            logger.error(f"Error fetching ESPN rankings: {e}")
            return {}
    
    def get_team_stats(self, team_id):
        """Fetch stats for a specific team"""
        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            team = data.get('team', {})
            return {
                'id': team.get('id'),
                'name': team.get('displayName'),
                'logo': team.get('logo'),
                'record': team.get('record'),
                'location': team.get('location'),
                'color': team.get('color')
            }
        except Exception as e:
            logger.error(f"Error fetching team stats for {team_id}: {e}")
            return {}
    
    def get_schedule(self):
        """Fetch current season schedule and results"""
        try:
            url = f"{self.BASE_URL}/scoreboard"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                for comp in event.get('competitions', []):
                    game = {
                        'id': comp.get('id'),
                        'date': comp.get('date'),
                        'home_team': None,
                        'away_team': None,
                        'home_score': None,
                        'away_score': None
                    }
                    
                    for competitor in comp.get('competitors', []):
                        is_home = competitor.get('homeAway') == 'home'
                        team_info = competitor.get('team', {})
                        score = competitor.get('score')
                        
                        team_name = team_info.get('displayName') or team_info.get('name')
                        team_id = team_info.get('id') or competitor.get('id')
                        
                        team_data = {
                            'id': team_id,
                            'name': team_name,
                            'score': score
                        }
                        
                        if is_home:
                            game['home_team'] = team_data
                            game['home_score'] = score
                        else:
                            game['away_team'] = team_data
                            game['away_score'] = score
                    
                    # Only include games with complete data
                    if game['home_team'] and game['away_team'] and game['home_score'] is not None and game['away_score'] is not None:
                        games.append(game)
            
            logger.info(f"Fetched {len(games)} games from schedule")
            return games
        except Exception as e:
            logger.error(f"Error fetching schedule: {e}")
            return []
