import requests
import json
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ESPNScraper:
    """Scrape NCAA basketball data from ESPN"""
    
    @staticmethod
    def _parse_score(score_raw):
        """Parse score from ESPN API - handles both string and dict formats."""
        if score_raw is None:
            return None
        if isinstance(score_raw, dict):
            # Schedule endpoint returns {'value': 75.0, 'displayValue': '75'}
            val = score_raw.get('value', score_raw.get('displayValue'))
            return int(float(val)) if val is not None else None
        if isinstance(score_raw, (int, float)):
            return int(score_raw)
        if isinstance(score_raw, str):
            try:
                return int(score_raw)
            except ValueError:
                return None
        return None
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball"
    
    def get_rankings(self):
        """
        Fetch current AP Top 25 + others receiving votes.
        Returns dict keyed by team_id with name, short_name, rank, points, record info.
        """
        try:
            url = f"{self.BASE_URL}/rankings"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            rankings = {}
            if 'rankings' in data:
                # Use AP Top 25 (first ranking group)
                for rank_group in data['rankings']:
                    group_name = rank_group.get('name', '')
                    
                    # Process ranked teams (in 'ranks', not 'entries')
                    for rank_entry in rank_group.get('ranks', []):
                        team = rank_entry.get('team', {})
                        team_id = str(team.get('id', ''))
                        if not team_id:
                            continue
                        
                        location = team.get('location', '')
                        name = team.get('name', '')
                        nickname = team.get('nickname', location)
                        display_name = f"{location} {name}".strip()
                        
                        rankings[team_id] = {
                            'name': display_name,
                            'short_name': location,
                            'nickname': nickname,
                            'abbreviation': team.get('abbreviation', ''),
                            'rank': rank_entry.get('current'),
                            'previous_rank': rank_entry.get('previous'),
                            'points': rank_entry.get('points'),
                            'first_place_votes': rank_entry.get('firstPlaceVotes', 0),
                            'trend': rank_entry.get('trend', ''),
                            'poll': group_name
                        }
                    
                    # Also grab "others receiving votes"
                    for other_entry in rank_group.get('others', []):
                        team = other_entry.get('team', {})
                        team_id = str(team.get('id', ''))
                        if not team_id or team_id in rankings:
                            continue
                        
                        location = team.get('location', '')
                        name = team.get('name', '')
                        nickname = team.get('nickname', location)
                        display_name = f"{location} {name}".strip()
                        
                        rankings[team_id] = {
                            'name': display_name,
                            'short_name': location,
                            'nickname': nickname,
                            'abbreviation': team.get('abbreviation', ''),
                            'rank': None,  # Not ranked, but receiving votes
                            'previous_rank': other_entry.get('previous'),
                            'points': other_entry.get('points'),
                            'first_place_votes': 0,
                            'trend': other_entry.get('trend', ''),
                            'poll': group_name
                        }
                    
                    # Only use first poll (AP Top 25) to avoid duplicates
                    break
            
            logger.info(f"Fetched {len(rankings)} teams from ESPN rankings (ranked + others receiving votes)")
            return rankings
        except Exception as e:
            logger.error(f"Error fetching ESPN rankings: {e}")
            return {}
    
    def get_team_record(self, team_id):
        """
        Fetch detailed record for a specific team.
        Returns wins, losses, record summary, points for/against, etc.
        """
        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            team = data.get('team', {})
            record_data = team.get('record', {})
            
            result = {
                'id': str(team.get('id', '')),
                'name': team.get('displayName', ''),
                'short_name': team.get('location', ''),
                'abbreviation': team.get('abbreviation', ''),
                'rank': team.get('rank', None),
                'wins': 0,
                'losses': 0,
                'record_summary': '',
                'games_played': 0,
                'avg_points_for': 0.0,
                'avg_points_against': 0.0,
                'point_differential': 0.0,
                'streak': 0,
                'conference_record': '',
            }
            
            # Parse record items
            for item in record_data.get('items', []):
                rec_type = item.get('type', '')
                stats_dict = {}
                for stat in item.get('stats', []):
                    stats_dict[stat['name']] = stat['value']
                
                if rec_type == 'total':
                    result['record_summary'] = item.get('summary', '')
                    result['wins'] = int(stats_dict.get('wins', 0))
                    result['losses'] = int(stats_dict.get('losses', 0))
                    result['games_played'] = int(stats_dict.get('gamesPlayed', 0))
                    result['avg_points_for'] = stats_dict.get('avgPointsFor', 0.0)
                    result['avg_points_against'] = stats_dict.get('avgPointsAgainst', 0.0)
                    result['point_differential'] = stats_dict.get('differential', 0.0)
                    result['streak'] = int(stats_dict.get('streak', 0))
                elif rec_type == 'vsconf':
                    result['conference_record'] = item.get('summary', '')
            
            return result
        except Exception as e:
            logger.error(f"Error fetching team record for {team_id}: {e}")
            return {}
    
    def get_team_schedule(self, team_id):
        """
        Fetch full season schedule/results for a team.
        Returns list of completed games with scores.
        """
        try:
            url = f"{self.BASE_URL}/teams/{team_id}/schedule"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                comps = event.get('competitions', [])
                if not comps:
                    continue
                comp = comps[0]
                
                # Only include completed games
                status = comp.get('status', {}).get('type', {}).get('name', '')
                if status != 'STATUS_FINAL':
                    continue
                
                game = {
                    'id': comp.get('id'),
                    'date': comp.get('date', event.get('date')),
                    'home_team': None,
                    'away_team': None,
                    'home_score': None,
                    'away_score': None,
                    'neutral_site': comp.get('neutralSite', False),
                }
                
                for competitor in comp.get('competitors', []):
                    is_home = competitor.get('homeAway') == 'home'
                    team_info = competitor.get('team', {})
                    score = competitor.get('score')
                    
                    team_data = {
                        'id': str(team_info.get('id', '')),
                        'name': team_info.get('displayName', f"{team_info.get('location', '')} {team_info.get('name', '')}".strip()),
                        'short_name': team_info.get('location', team_info.get('displayName', '')),
                        'score': self._parse_score(score),
                    }
                    
                    if is_home:
                        game['home_team'] = team_data
                        game['home_score'] = team_data['score']
                    else:
                        game['away_team'] = team_data
                        game['away_score'] = team_data['score']
                
                if game['home_team'] and game['away_team'] and game['home_score'] is not None and game['away_score'] is not None:
                    games.append(game)
            
            logger.info(f"Fetched {len(games)} completed games for team {team_id}")
            return games
        except Exception as e:
            logger.error(f"Error fetching schedule for team {team_id}: {e}")
            return []
    
    def get_schedule(self):
        """Fetch today's scoreboard (for live game tracking)"""
        try:
            url = f"{self.BASE_URL}/scoreboard"
            response = requests.get(url, timeout=15)
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
                        
                        team_name = team_info.get('displayName') or f"{team_info.get('location', '')} {team_info.get('name', '')}".strip()
                        team_id = str(team_info.get('id', competitor.get('id', '')))
                        
                        team_data = {
                            'id': team_id,
                            'name': team_name,
                            'short_name': team_info.get('location', team_name),
                            'score': score
                        }
                        
                        if is_home:
                            game['home_team'] = team_data
                            game['home_score'] = score
                        else:
                            game['away_team'] = team_data
                            game['away_score'] = score
                    
                    if game['home_team'] and game['away_team']:
                        games.append(game)
            
            logger.info(f"Fetched {len(games)} games from today's scoreboard")
            return games
        except Exception as e:
            logger.error(f"Error fetching schedule: {e}")
            return []
    
    def get_all_ranked_team_data(self):
        """
        Comprehensive data fetch: rankings + records + schedules for all ranked teams.
        Returns dict keyed by team_id with full data.
        Rate-limited to be polite to ESPN API.
        """
        rankings = self.get_rankings()
        
        all_data = {}
        total = len(rankings)
        
        for i, (team_id, rank_info) in enumerate(rankings.items()):
            logger.info(f"  Fetching data for {rank_info['short_name']} ({i+1}/{total})...")
            
            # Get record
            record = self.get_team_record(team_id)
            
            # Get schedule (game results)
            schedule = self.get_team_schedule(team_id)
            
            all_data[team_id] = {
                **rank_info,
                'record': record,
                'schedule': schedule,
            }
            
            # Rate limit: 0.3s between requests to be polite
            if i < total - 1:
                time.sleep(0.3)
        
        logger.info(f"Fetched complete data for {len(all_data)} teams")
        return all_data
