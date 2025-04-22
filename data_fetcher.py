import requests
import pandas as pd
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBADataFetcher:
    def __init__(self):
        self.base_url = "https://api.balldontlie.io/v1"
        self.cache = {}
        self.cache_expiry = {}
        
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
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to the NBA API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Authorization': 'Bearer YOUR_API_KEY'  # Replace with actual API key
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {endpoint}: {str(e)}")
            return {}
            
    def get_active_players(self) -> List[str]:
        """Get list of active NBA players"""
        cache_key = "active_players"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            # Get all players
            data = self._make_request("players")
            players = data.get('data', [])
            
            # Filter for active players
            active_players = [
                f"{player['first_name']} {player['last_name']}"
                for player in players
                if player.get('active', False)
            ]
            
            self._set_cache(cache_key, active_players)
            return active_players
            
        except Exception as e:
            logger.error(f"Error getting active players: {str(e)}")
            return []
            
    def get_player_stats(self, player_name: str) -> Optional[pd.Series]:
        """Get current season stats for a player"""
        cache_key = f"player_stats_{player_name}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return pd.Series(cached_data)
            
        try:
            # Get player ID
            first_name, last_name = player_name.split(' ', 1)
            params = {
                'search': player_name,
                'per_page': 1
            }
            data = self._make_request("players", params)
            players = data.get('data', [])
            
            if not players:
                logger.warning(f"Player not found: {player_name}")
                return None
                
            player_id = players[0]['id']
            
            # Get current season stats
            current_season = datetime.now().year
            params = {
                'player_ids[]': player_id,
                'seasons[]': current_season,
                'per_page': 1
            }
            data = self._make_request("season_averages", params)
            stats = data.get('data', [])
            
            if not stats:
                logger.warning(f"No stats found for {player_name}")
                return None
                
            # Convert stats to Series
            stats_series = pd.Series(stats[0])
            
            # Calculate additional metrics
            stats_series['TS_PCT'] = self._calculate_true_shooting(
                stats_series.get('pts', 0),
                stats_series.get('fgm', 0),
                stats_series.get('fga', 0),
                stats_series.get('ftm', 0),
                stats_series.get('fta', 0)
            )
            
            # Cache the stats
            self._set_cache(cache_key, stats_series.to_dict())
            
            return stats_series
            
        except Exception as e:
            logger.error(f"Error getting stats for {player_name}: {str(e)}")
            return None
            
    def _calculate_true_shooting(self, pts: float, fgm: float, fga: float, ftm: float, fta: float) -> float:
        """Calculate true shooting percentage"""
        if fga + 0.44 * fta == 0:
            return 0
        return pts / (2 * (fga + 0.44 * fta))
        
    def get_team_performance(self, team_id: int) -> Dict:
        """Get team performance metrics"""
        cache_key = f"team_performance_{team_id}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            # Get team stats
            params = {
                'team_ids[]': team_id,
                'seasons[]': datetime.now().year,
                'per_page': 1
            }
            data = self._make_request("team_stats", params)
            stats = data.get('data', [])
            
            if not stats:
                return {}
                
            # Cache the stats
            self._set_cache(cache_key, stats[0])
            
            return stats[0]
            
        except Exception as e:
            logger.error(f"Error getting team performance for {team_id}: {str(e)}")
            return {}
            
    def get_top_scorers(self, limit: int = 10) -> List[Dict]:
        """Get top scorers in the league"""
        cache_key = f"top_scorers_{limit}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            # Get all players' season averages
            params = {
                'seasons[]': datetime.now().year,
                'per_page': 100
            }
            data = self._make_request("season_averages", params)
            stats = data.get('data', [])
            
            # Sort by points and get top scorers
            top_scorers = sorted(stats, key=lambda x: x.get('pts', 0), reverse=True)[:limit]
            
            # Cache the results
            self._set_cache(cache_key, top_scorers)
            
            return top_scorers
            
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
            # Get all players' season averages
            params = {
                'seasons[]': datetime.now().year,
                'per_page': 100
            }
            data = self._make_request("season_averages", params)
            stats = data.get('data', [])
            
            # Sort by points and get bottom scorers
            bottom_scorers = sorted(stats, key=lambda x: x.get('pts', 0))[:limit]
            
            # Cache the results
            self._set_cache(cache_key, bottom_scorers)
            
            return bottom_scorers
            
        except Exception as e:
            logger.error(f"Error getting bottom scorers: {str(e)}")
            return [] 