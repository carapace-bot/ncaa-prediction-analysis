import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolymarketAnalyzer:
    """Analyze NCAA tournament prediction markets on Polymarket"""
    
    POLYMARKET_API = "https://clob.polymarket.com"
    
    def search_markets(self, query="NCAA"):
        """Search for NCAA-related markets on Polymarket"""
        try:
            url = f"{self.POLYMARKET_API}/markets"
            params = {"search": query}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            markets = []
            if isinstance(data, list):
                markets = data
            elif isinstance(data, dict) and 'markets' in data:
                markets = data['markets']
            
            logger.info(f"Found {len(markets)} NCAA markets on Polymarket")
            return markets
        except Exception as e:
            logger.error(f"Error searching Polymarket: {e}")
            return []
    
    def get_market_details(self, market_id):
        """Get detailed info on a specific market"""
        try:
            url = f"{self.POLYMARKET_API}/markets/{market_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return {}
    
    def get_order_book(self, market_id):
        """Get current order book for a market"""
        try:
            url = f"{self.POLYMARKET_API}/markets/{market_id}/orderbook"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data
        except Exception as e:
            logger.error(f"Error fetching orderbook for {market_id}: {e}")
            return {}
    
    def extract_implied_odds(self, market):
        """Extract implied probability from market data"""
        try:
            odds = {}
            
            # Structure varies by market type
            if 'outcomes' in market:
                for outcome in market['outcomes']:
                    name = outcome.get('name', outcome.get('title'))
                    price = outcome.get('price', outcome.get('prob'))
                    
                    if name and price is not None:
                        odds[name] = float(price)
            
            return odds
        except Exception as e:
            logger.error(f"Error extracting odds: {e}")
            return {}
    
    def find_mispricing(self, model_odds, market_odds, min_edge=0.05):
        """
        Identify mispricings between model and market.
        
        model_odds: dict of {outcome: model_probability}
        market_odds: dict of {outcome: market_probability}
        min_edge: minimum edge to consider significant
        
        Returns: list of {outcome, model_prob, market_prob, edge, direction}
        """
        mispricings = []
        
        for outcome in model_odds:
            if outcome not in market_odds:
                continue
            
            model_prob = model_odds[outcome]
            market_prob = market_odds[outcome]
            
            edge = model_prob - market_prob
            
            # Positive edge: market underprices (good BUY)
            # Negative edge: market overprices (good SELL)
            
            if abs(edge) >= min_edge:
                mispricings.append({
                    'outcome': outcome,
                    'model_probability': model_prob,
                    'market_probability': market_prob,
                    'edge': edge,
                    'direction': 'BUY' if edge > 0 else 'SELL',
                    'expected_value': edge * (1 - market_prob) if edge > 0 else edge * market_prob
                })
        
        # Sort by expected value (absolute)
        mispricings.sort(key=lambda x: abs(x['expected_value']), reverse=True)
        
        return mispricings
    
    def calculate_position_size(self, bankroll, edge, confidence=0.75):
        """
        Calculate appropriate position size using Kelly Criterion approximation
        
        bankroll: total capital
        edge: our assessed edge (probability difference)
        confidence: confidence level in the model (0-1)
        """
        if edge <= 0 or confidence <= 0:
            return 0
        
        # Kelly formula: f = (bp - q) / b
        # Simplified: edge * confidence is our effective edge
        effective_edge = edge * confidence
        
        # Never risk more than 5% per position
        max_position = bankroll * 0.05
        
        # Kelly-derived sizing (fractional kelly for safety)
        kelly_size = bankroll * effective_edge * 0.25  # Quarter kelly
        
        # Take minimum of kelly and hard limit
        position_size = min(kelly_size, max_position)
        
        return position_size
