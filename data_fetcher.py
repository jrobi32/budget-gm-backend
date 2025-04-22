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
            # Get player stats DataFrame
            df = self.get_player_stats()
            
            if df.empty:
                logger.error("No player stats available")
                return []
            
            # Ensure rating column exists
            if 'rating' not in df.columns:
                logger.error("Rating column not found in DataFrame")
                return []
            
            # Calculate percentiles for ratings
            df['percentile'] = df['rating'].rank(pct=True) * 100
            
            # Assign costs based on percentiles
            def get_cost(percentile):
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
            
            df['cost'] = df['percentile'].apply(get_cost)
            
            # Convert to list of dictionaries with selected stats
            players = []
            for _, row in df.iterrows():
                if row['GP'] > 0:  # Only include players who have played games
                    player = {
                        'name': row['PLAYER_NAME'],
                        'cost': row['cost'],
                        'rating': round(row['rating'], 1),
                        'stats': {
                            'pts': round(row['PTS'], 1),
                            'ast': round(row['AST'], 1),
                            'reb': round(row['REB'], 1),
                            'stl': round(row['STL'], 1),
                            'blk': round(row['BLK'], 1),
                            'fg_pct': round(row['FG_PCT'] * 100, 1),
                            'ts_pct': round(row['TS_PCT'] * 100, 1),
                            'gp': int(row['GP'])
                        }
                    }
                    players.append(player)
            
            # Log distribution of costs
            cost_distribution = df['cost'].value_counts().sort_index()
            logger.info(f"Player cost distribution: {cost_distribution.to_dict()}")
            
            return players
            
        except Exception as e:
            logger.error(f"Error getting active players: {str(e)}")
            return []
            
    def get_player_stats(self) -> pd.DataFrame:
        """Get player stats for a given season"""
        cache_key = 'player_stats'
        try:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return pd.DataFrame(cached_data)
                
            # Get all player stats in one request
            stats = self._make_api_call(
                leaguedashplayerstats.LeagueDashPlayerStats,
                measure_type_detailed_defense='Base',
                per_mode_detailed='PerGame',
                timeout=self.timeout
            )
            
            if not stats or not stats.get_data_frames():
                logger.error("Empty response from NBA API")
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(stats.get_data_frames()[0])
            if df.empty:
                logger.error("No player data in response")
                return pd.DataFrame()
                
            logger.info(f"Retrieved {len(df)} players from NBA API")
            
            # Calculate true shooting percentage
            df['TS_PCT'] = df.apply(
                lambda row: self._calculate_true_shooting(
                    row['PTS'],
                    row['FGM'],
                    row['FGA'],
                    row['FTM'],
                    row['FTA']
                ),
                axis=1
            )
            
            # Calculate player rating based on weighted stats
            weights = {
                'PTS': 1.0,
                'AST': 1.0,
                'REB': 0.8,
                'STL': 0.7,
                'BLK': 0.7,
                'FG_PCT': 0.5,
                'TS_PCT': 0.5
            }
            
            # Initialize rating column
            df['rating'] = 0
            
            # Add weighted contributions
            for stat, weight in weights.items():
                if stat in df.columns:
                    # Handle percentage stats
                    if stat in ['FG_PCT', 'TS_PCT']:
                        df['rating'] += df[stat].fillna(0) * weight * 100
                    else:
                        df['rating'] += df[stat].fillna(0) * weight
            
            # Add bonuses for exceptional performance
            df['rating'] += np.where(df['PTS'] >= 25, 10, 0)  # Bonus for high scorers
            df['rating'] += np.where(df['AST'] >= 8, 8, 0)    # Bonus for playmakers
            df['rating'] += np.where(df['REB'] >= 10, 8, 0)   # Bonus for rebounders
            df['rating'] += np.where(df['STL'] >= 2, 5, 0)    # Bonus for defenders
            df['rating'] += np.where(df['BLK'] >= 2, 5, 0)    # Bonus for rim protectors
            
            # Normalize ratings to 1-100 range
            min_rating = df['rating'].min()
            max_rating = df['rating'].max()
            if max_rating > min_rating:  # Avoid division by zero
                df['rating'] = ((df['rating'] - min_rating) / (max_rating - min_rating)) * 99 + 1
            else:
                df['rating'] = 50  # Default rating if all players have same score
            
            # Calculate percentiles for ratings
            df['percentile'] = df['rating'].rank(pct=True) * 100
            
            # Assign costs based on percentiles
            df['cost'] = df['percentile'].apply(self._get_cost_from_percentile)
            
            # Cache the results
            self._set_cache(cache_key, df.to_dict('records'))
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting player stats: {str(e)}")
            return pd.DataFrame()
            
    def _calculate_true_shooting(self, pts: float, fgm: float, fga: float, ftm: float, fta: float) -> float:
        """Calculate true shooting percentage"""
        if fga + 0.44 * fta == 0:
            return 0
        return pts / (2 * (fga + 0.44 * fta))
            
    def get_top_scorers(self, limit: int = 10) -> List[Dict]:
        """Get top scorers in the league"""
        cache_key = f"top_scorers_{limit}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            df = self.get_player_stats()
            if not df.empty and 'PTS' in df.columns:
                top_scorers = df.nlargest(limit, 'PTS')
                result = top_scorers[['PLAYER_NAME', 'PTS', 'REB', 'AST', 'TS_PCT']].to_dict('records')
            else:
                result = []
            
            # Cache the results
            self._set_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting top scorers: {str(e)}")
            return []
            
    def get_bottom_scorers(self, limit: int = 10) -> List[Dict]:
        """Get bottom scorers in the league"""
        cache_key = f"bottom_scorers_{limit}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            df = self.get_player_stats()
            if not df.empty and 'PTS' in df.columns:
                bottom_scorers = df.nsmallest(limit, 'PTS')
                result = bottom_scorers[['PLAYER_NAME', 'PTS', 'REB', 'AST', 'TS_PCT']].to_dict('records')
            else:
                result = []
            
            # Cache the results
            self._set_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting bottom scorers: {str(e)}")
            return []
            
    def calculate_player_cost(self, stats: Dict) -> str:
        """Calculate player cost based on rating percentiles"""
        try:
            # Get all player ratings
            df = self.get_player_stats()
            if df.empty:
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
            
            # Normalize to 1-100 range
            min_rating = df['rating'].min()
            max_rating = df['rating'].max()
            rating = ((rating - min_rating) / (max_rating - min_rating)) * 99 + 1
            
            # Calculate percentile
            percentile = (df['rating'] < rating).mean() * 100
            
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

    def get_player_pool(self) -> List[Dict]:
        """Get a list of active NBA players with their stats and costs"""
        try:
            # Get player stats DataFrame
            df = self.get_player_stats()
            
            if df.empty:
                logger.error("No player stats available")
                return []
            
            # Ensure rating column exists
            if 'rating' not in df.columns:
                logger.error("Rating column not found in DataFrame")
                return []
            
            # Calculate percentiles for ratings
            df['percentile'] = df['rating'].rank(pct=True) * 100
            
            # Assign costs based on percentiles
            def get_cost(percentile):
                if percentile >= 80: return '5'
                elif percentile >= 60: return '4'
                elif percentile >= 40: return '3'
                elif percentile >= 20: return '2'
                else: return '1'
            
            # Convert DataFrame to list of dictionaries efficiently
            players = []
            for _, row in df.iterrows():
                player = {
                    'name': row['PLAYER_NAME'],
                    'id': row['PLAYER_ID'],
                    'cost': get_cost(row['percentile']),
                    'stats': {
                        'pts': float(row.get('PTS', 0)),
                        'ast': float(row.get('AST', 0)),
                        'reb': float(row.get('REB', 0)),
                        'stl': float(row.get('STL', 0)),
                        'blk': float(row.get('BLK', 0)),
                        'fg_pct': float(row.get('FG_PCT', 0)),
                        'three_pct': float(row.get('FG3_PCT', 0))
                    }
                }
                players.append(player)
            
            logger.info(f"Loaded {len(players)} players from today's pool")
            return players
            
        except Exception as e:
            logger.error(f"Error in get_player_pool: {str(e)}")
            return [] 