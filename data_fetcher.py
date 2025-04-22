from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from requests.exceptions import RequestException
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBADataFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.max_retries = 3
        self.retry_delay = 5
        self.timeout = 30
        
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache if it's not expired"""
        if key in self.cache and key in self.cache_expiry:
            if datetime.now() < self.cache_expiry[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.cache_expiry[key]
        return None
        
    def _set_cache(self, key: str, data: Dict, expiry_hours: int = 24):
        """Set data in cache with expiry time"""
        self.cache[key] = data
        self.cache_expiry[key] = datetime.now() + timedelta(hours=expiry_hours)
        
    def _make_api_call(self, func, *args, **kwargs):
        """Make API call with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Add random delay between retries
                if attempt > 0:
                    time.sleep(self.retry_delay + random.uniform(1, 3))
                return func(*args, **kwargs)
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"API call failed after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
        
    def get_active_players(self) -> List[str]:
        """Get list of active NBA players"""
        cache_key = "active_players"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            # Get all players with their stats
            stats = self._make_api_call(
                leaguedashplayerstats.LeagueDashPlayerStats,
                measure_type_detailed_defense='Base',
                per_mode_detailed='PerGame',
                timeout=self.timeout
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(stats.get_data_frames()[0])
            
            # Get active players (those who have played at least one game)
            active_players = df[df['GP'] > 0]['PLAYER_NAME'].tolist()
            
            # Cache the results
            self._set_cache(cache_key, active_players)
            
            return active_players
            
        except Exception as e:
            logger.error(f"Error getting active players: {str(e)}")
            return []
            
    def get_player_stats(self, season: str = None) -> pd.DataFrame:
        """Get player stats for a given season"""
        if season is None:
            current_year = datetime.now().year
            current_month = datetime.now().month
            season = f"{current_year-1}-{str(current_year)[2:]}" if current_month < 10 else f"{current_year}-{str(current_year+1)[2:]}"
            
        cache_key = f"player_stats_{season}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return pd.DataFrame(cached_data)
            
        try:
            # Get all player stats in one request
            stats = self._make_api_call(
                leaguedashplayerstats.LeagueDashPlayerStats,
                measure_type_detailed_defense='Base',
                per_mode_detailed='PerGame',
                timeout=self.timeout
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(stats.get_data_frames()[0])
            
            if not df.empty:
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
                
                # Cache the results
                self._set_cache(cache_key, df.to_dict())
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting player stats: {str(e)}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['PLAYER_NAME', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'TS_PCT', 'GP'])
            
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
            
    def calculate_player_cost(self, stats: Dict) -> int:
        """Calculate player cost based on performance metrics"""
        # Weights for different statistics
        weights = {
            'PTS': 1.0,
            'REB': 0.7,
            'AST': 0.7,
            'STL': 0.5,
            'BLK': 0.5,
            'FG_PCT': 0.4,
            'FG3_PCT': 0.3,
            'FT_PCT': 0.3,
            'TOV': -0.3,
            'GP': 0.1
        }
        
        # Calculate weighted score
        score = (
            stats['PTS'] * weights['PTS'] +
            stats['REB'] * weights['REB'] +
            stats['AST'] * weights['AST'] +
            stats['STL'] * weights['STL'] +
            stats['BLK'] * weights['BLK'] +
            stats['FG_PCT'] * weights['FG_PCT'] * 100 +
            stats['FG3_PCT'] * weights['FG3_PCT'] * 100 +
            stats['FT_PCT'] * weights['FT_PCT'] * 100 -
            stats['TOV'] * weights['TOV'] +
            stats['GP'] * weights['GP']
        )
        
        # Normalize score to 1-5 range
        if score > 50:
            return 5
        elif score > 40:
            return 4
        elif score > 30:
            return 3
        elif score > 20:
            return 2
        else:
            return 1 