from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from requests.exceptions import RequestException
import random
import json
import os
import gc
from .static_player_pool import get_static_player_pool, get_players_by_cost, get_all_players
from .player_stats import get_player_stats, get_all_player_stats, get_player_3_season_avg, get_all_player_3_season_avg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBADataFetcher:
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        self.cache_duration = timedelta(hours=24)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.max_retries = 5
        self.retry_delay = 10
        self.timeout = 60
        
    def _get_cost_from_percentile(self, percentile: float) -> str:
        """Calculate player cost based on percentile"""
        if percentile >= 95:    # Top 5%
            return '$5'
        elif percentile >= 80:  # Next 15%
            return '$4'
        elif percentile >= 60:  # Next 20%
            return '$3'
        elif percentile >= 30:  # Next 30%
            return '$2'
        else:                   # Bottom 30%
            return '$1'
            
    def _get_from_cache(self, cache_key):
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    if datetime.fromisoformat(cached_data['timestamp']) + self.cache_duration > datetime.now():
                        return cached_data['data']
            return None
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None

    def _set_cache(self, cache_key, data):
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
        
    def _make_api_call(self, func, *args, **kwargs):
        """Make API call with retry logic"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Referer': 'https://stats.nba.com/',
            'Connection': 'keep-alive',
            'Host': 'stats.nba.com'
        }
        
        for attempt in range(self.max_retries):
            try:
                # Add random delay between retries
                if attempt > 0:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay + random.uniform(1, 3))
                    
                # Add headers to kwargs
                if 'headers' in kwargs:
                    kwargs['headers'].update(headers)
                else:
                    kwargs['headers'] = headers
                    
                # Add timeout to kwargs
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout
                    
                response = func(*args, **kwargs)
                if response is None:
                    raise RequestException("Empty response from API")
                return response
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"API call failed after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error in API call: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
        
    def get_active_players(self) -> List[Dict]:
        """Get a list of active NBA players with their stats and costs"""
        try:
            # Use static player pool instead of making API calls
            return get_all_players()
        except Exception as e:
            logger.error(f"Error getting active players: {str(e)}")
            return []
            
    def get_player_pool(self) -> List[Dict]:
        """Get a curated player pool optimized for the game"""
        try:
            # Use static player pool instead of making API calls
            return get_all_players()
        except Exception as e:
            logger.error(f"Error generating player pool: {str(e)}")
            return []
            
    def get_player_stats(self) -> pd.DataFrame:
        """Get player stats for a given season"""
        try:
            # Convert static player pool to DataFrame
            players = get_all_players()
            if not players:
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(players)
            
            # Explode stats dictionary into columns
            stats_df = pd.json_normalize(df['stats'])
            df = pd.concat([df.drop(['stats'], axis=1), stats_df], axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting player stats: {str(e)}")
            return pd.DataFrame()

    def get_player_3_season_avg(self, player_name: str) -> Dict:
        """Get 3-season average stats for a specific player"""
        try:
            return get_player_3_season_avg(player_name)
        except Exception as e:
            logger.error(f"Error getting 3-season average for {player_name}: {str(e)}")
            return {}

    def get_all_player_3_season_avg(self) -> Dict:
        """Get 3-season average stats for all players"""
        try:
            return get_all_player_3_season_avg()
        except Exception as e:
            logger.error(f"Error getting all player 3-season averages: {str(e)}")
            return {}

    def get_player_details(self, player_name: str) -> Dict:
        """Get detailed player information including current and 3-season average stats"""
        try:
            return get_player_stats(player_name)
        except Exception as e:
            logger.error(f"Error getting details for {player_name}: {str(e)}")
            return {}
            
    def get_all_player_details(self) -> Dict:
        """Get detailed information for all players"""
        try:
            return get_all_player_stats()
        except Exception as e:
            logger.error(f"Error getting all player details: {str(e)}")
            return {}
            
    def calculate_player_cost(self, stats: Dict) -> str:
        """Calculate player cost based on rating percentiles"""
        try:
            # Get all players
            players = get_all_players()
            if not players:
                return '$1'
            
            # Calculate the rating for this player
            weights = {
                'PTS': 1.0,
                'AST': 1.0,
                'REB': 0.8,
                'STL': 0.7,
                'BLK': 0.7,
                'FG_PCT': 0.5,
                'TS_PCT': 0.5
            }
            
            rating = 0
            for stat, weight in weights.items():
                if stat in stats:
                    if stat in ['FG_PCT', 'TS_PCT']:
                        rating += float(stats[stat]) * weight * 100
                    else:
                        rating += float(stats[stat]) * weight
            
            # Add bonuses
            if float(stats.get('PTS', 0)) >= 25: rating += 10
            if float(stats.get('AST', 0)) >= 8: rating += 8
            if float(stats.get('REB', 0)) >= 10: rating += 8
            if float(stats.get('STL', 0)) >= 2: rating += 5
            if float(stats.get('BLK', 0)) >= 2: rating += 5
            
            # Get all ratings
            all_ratings = [p['rating'] for p in players]
            
            # Calculate percentile
            percentile = (sum(1 for r in all_ratings if r < rating) / len(all_ratings)) * 100
            
            # Assign cost based on percentile ranges
            if percentile >= 95:    # Top 5%
                return '$5'
            elif percentile >= 80:  # Next 15%
                return '$4'
            elif percentile >= 60:  # Next 20%
                return '$3'
            elif percentile >= 30:  # Next 30%
                return '$2'
            else:                   # Bottom 30%
                return '$1'
                
        except Exception as e:
            logger.error(f"Error calculating player cost: {str(e)}")
            return '$1'

    def get_top_scorers(self, limit: int = 10) -> List[Dict]:
        """Get top scorers in the league"""
        try:
            players = get_all_players()
            if not players:
                return []
            
            # Sort by points and get top limit
            top_scorers = sorted(players, key=lambda x: x['stats']['pts'], reverse=True)[:limit]
            return top_scorers
            
        except Exception as e:
            logger.error(f"Error getting top scorers: {str(e)}")
            return []
            
    def get_bottom_scorers(self, limit: int = 10) -> List[Dict]:
        """Get bottom scorers in the league"""
        try:
            players = get_all_players()
            if not players:
                return []
            
            # Sort by points and get bottom limit
            bottom_scorers = sorted(players, key=lambda x: x['stats']['pts'])[:limit]
            return bottom_scorers
            
        except Exception as e:
            logger.error(f"Error getting bottom scorers: {str(e)}")
            return []

    def store_categorized_players(self, players: List[Dict]) -> None:
        """Store players in a categorized format by cost"""
        try:
            categorized_players = {
                '$5': [],
                '$4': [],
                '$3': [],
                '$2': [],
                '$1': []
            }
            
            # Process players in chunks
            chunk_size = 100
            for i in range(0, len(players), chunk_size):
                chunk = players[i:i + chunk_size]
                for player in chunk:
                    cost = player.get('cost', '$1')
                    if cost in categorized_players:
                        # Only store essential data
                        categorized_players[cost].append({
                            'name': player['name'],
                            'id': player['id'],
                            'stats': player['stats']
                        })
            
                # Force garbage collection after each chunk
                del chunk
                gc.collect()
                
                # Add small delay between chunks
                time.sleep(0.1)
            
            # Store the categorized players
            cache_file = os.path.join(self.cache_dir, 'categorized_players.json')
            with open(cache_file, 'w') as f:
                json.dump(categorized_players, f)
            
            logger.info(f"Stored {len(players)} players in categorized format")
            
        except Exception as e:
            logger.error(f"Error storing categorized players: {str(e)}")
        finally:
            # Force garbage collection
            gc.collect()

    def get_categorized_players(self) -> Dict[str, List[Dict]]:
        """Get players from the categorized cache"""
        try:
            cache_file = os.path.join(self.cache_dir, 'categorized_players.json')
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
            return {
                '$5': [],
                '$4': [],
                '$3': [],
                '$2': [],
                '$1': []
            }
        except Exception as e:
            logger.error(f"Error reading categorized players: {str(e)}")
            return {
                '$5': [],
                '$4': [],
                '$3': [],
                '$2': [],
                '$1': []
            } 