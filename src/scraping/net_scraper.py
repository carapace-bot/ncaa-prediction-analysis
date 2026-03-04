import requests
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NETScraper:
    """Scrape NCAA NET rankings from NCAA.org"""
    
    # NCAA NET rankings are published at: https://www.ncaa.org/news
    # We'll use a fallback to historical data structure
    
    def parse_net_rankings(self, html):
        """Parse NET rankings from HTML table"""
        soup = BeautifulSoup(html, 'html.parser')
        rankings = {}
        
        try:
            # Look for ranking tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        try:
                            rank = cols[0].text.strip()
                            team_name = cols[1].text.strip()
                            # Parse wins-losses if present
                            record = cols[2].text.strip() if len(cols) > 2 else None
                            
                            rankings[team_name] = {
                                'rank': rank,
                                'record': record
                            }
                        except:
                            continue
        except Exception as e:
            logger.error(f"Error parsing NET rankings: {e}")
        
        return rankings
    
    def get_historical_net_rankings(self):
        """
        Get approximate NET rankings from public data.
        NCAA.org publishes these, but structure varies by year.
        This uses a best-effort approach to estimate current rankings.
        """
        try:
            # Try to fetch from NCAA tourney page which lists seedings
            url = "https://www.ncaa.org/news/2024/3/17/ncaa-tournament-bracket"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            rankings = self.parse_net_rankings(response.text)
            logger.info(f"Fetched {len(rankings)} teams from NET rankings")
            return rankings
        except Exception as e:
            logger.warning(f"Could not fetch live NET rankings: {e}")
            return {}
    
    def estimate_net_from_espn(self, espn_rankings):
        """
        Use ESPN power rankings as proxy for NET rankings
        when live NET data is unavailable
        """
        net_estimates = {}
        
        for team_id, team_data in espn_rankings.items():
            net_estimates[team_data['name']] = {
                'rank': team_data.get('rank'),
                'source': 'ESPN_power_ranking'
            }
        
        return net_estimates
