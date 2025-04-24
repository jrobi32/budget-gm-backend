"""
Player stats data for the NBA Team Builder game.
This file contains all players with their 3-season average stats.
"""

import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .static_player_pool import get_static_player_pool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache for player stats
_player_stats_cache = {}
_last_cache_update = 0
CACHE_DURATION = 3600  # 1 hour in seconds

PLAYER_STATS = {
    'Nikola Jokic': {
        'name': 'Nikola Jokic',
        'position': 'C',
        'team': 'DEN',
        'cost': '$5',
        'rating': 98.5,
        'stats': {
            'pts': 26.4,
            'ast': 9.0,
            'reb': 12.4,
            'stl': 1.4,
            'blk': 0.9,
            'fg_pct': 58.3,
            'ts_pct': 66.1,
            'gp': 69,
            '3pt_pct': 35.2,
            'ft_pct': 82.1,
            'tov': 3.2,
            'plus_minus': 8.5
        },
        '3_season_avg': {
            'pts': 25.8,
            'ast': 8.7,
            'reb': 12.1,
            'stl': 1.3,
            'blk': 0.8,
            'fg_pct': 57.5,
            'ts_pct': 65.8,
            'gp': 68,
            '3pt_pct': 34.8,
            'ft_pct': 81.9,
            'tov': 3.1,
            'plus_minus': 8.2
        }
    },
    'Giannis Antetokounmpo': {
        'name': 'Giannis Antetokounmpo',
        'position': 'PF',
        'team': 'MIL',
        'cost': '$5',
        'rating': 97.8,
        'stats': {
            'pts': 30.4,
            'ast': 6.5,
            'reb': 11.5,
            'stl': 1.2,
            'blk': 1.1,
            'fg_pct': 61.1,
            'ts_pct': 64.5,
            'gp': 63,
            '3pt_pct': 27.5,
            'ft_pct': 65.3,
            'tov': 3.4,
            'plus_minus': 7.8
        },
        '3_season_avg': {
            'pts': 29.8,
            'ast': 6.2,
            'reb': 11.2,
            'stl': 1.1,
            'blk': 1.0,
            'fg_pct': 60.5,
            'ts_pct': 63.9,
            'gp': 61,
            '3pt_pct': 26.8,
            'ft_pct': 64.8,
            'tov': 3.3,
            'plus_minus': 7.5
        }
    },
    'Devin Booker': {
        'name': 'Devin Booker',
        'position': 'SG',
        'team': 'PHX',
        'cost': '$4',
        'rating': 89.2,
        'stats': {
            'pts': 27.8,
            'ast': 5.5,
            'reb': 4.5,
            'stl': 1.0,
            'blk': 0.3,
            'fg_pct': 49.4,
            'ts_pct': 58.4,
            'gp': 53,
            '3pt_pct': 35.1,
            'ft_pct': 85.6,
            'tov': 2.8,
            'plus_minus': 5.2
        },
        '3_season_avg': {
            'pts': 26.9,
            'ast': 5.2,
            'reb': 4.3,
            'stl': 0.9,
            'blk': 0.3,
            'fg_pct': 48.8,
            'ts_pct': 57.9,
            'gp': 51,
            '3pt_pct': 34.7,
            'ft_pct': 85.2,
            'tov': 2.7,
            'plus_minus': 5.0
        }
    },
    'Jalen Brunson': {
        'name': 'Jalen Brunson',
        'position': 'PG',
        'team': 'NYK',
        'cost': '$3',
        'rating': 82.5,
        'stats': {
            'pts': 24.0,
            'ast': 6.2,
            'reb': 3.5,
            'stl': 0.9,
            'blk': 0.2,
            'fg_pct': 47.5,
            'ts_pct': 59.1,
            'gp': 77,
            '3pt_pct': 41.6,
            'ft_pct': 84.7,
            'tov': 2.1,
            'plus_minus': 3.8
        },
        '3_season_avg': {
            'pts': 22.8,
            'ast': 5.9,
            'reb': 3.3,
            'stl': 0.8,
            'blk': 0.2,
            'fg_pct': 47.0,
            'ts_pct': 58.6,
            'gp': 75,
            '3pt_pct': 40.8,
            'ft_pct': 84.2,
            'tov': 2.0,
            'plus_minus': 3.5
        }
    },
    'Bogdan Bogdanovic': {
        'name': 'Bogdan Bogdanovic',
        'position': 'SG',
        'team': 'ATL',
        'cost': '$2',
        'rating': 75.8,
        'stats': {
            'pts': 14.0,
            'ast': 2.6,
            'reb': 3.1,
            'stl': 1.2,
            'blk': 0.2,
            'fg_pct': 45.2,
            'ts_pct': 58.3,
            'gp': 59,
            '3pt_pct': 37.1,
            'ft_pct': 84.2,
            'tov': 1.5,
            'plus_minus': 1.2
        },
        '3_season_avg': {
            'pts': 13.8,
            'ast': 2.5,
            'reb': 3.0,
            'stl': 1.1,
            'blk': 0.2,
            'fg_pct': 44.9,
            'ts_pct': 58.0,
            'gp': 57,
            '3pt_pct': 36.8,
            'ft_pct': 83.9,
            'tov': 1.4,
            'plus_minus': 1.0
        }
    },
    'Jalen Williams': {
        'name': 'Jalen Williams',
        'position': 'SF',
        'team': 'OKC',
        'cost': '$1',
        'rating': 68.4,
        'stats': {
            'pts': 12.7,
            'ast': 3.3,
            'reb': 4.1,
            'stl': 1.4,
            'blk': 0.5,
            'fg_pct': 52.1,
            'ts_pct': 62.8,
            'gp': 75,
            '3pt_pct': 35.6,
            'ft_pct': 81.2,
            'tov': 1.8,
            'plus_minus': 0.8
        },
        '3_season_avg': {
            'pts': 12.5,
            'ast': 3.2,
            'reb': 4.0,
            'stl': 1.3,
            'blk': 0.5,
            'fg_pct': 51.8,
            'ts_pct': 62.5,
            'gp': 73,
            '3pt_pct': 35.2,
            'ft_pct': 80.9,
            'tov': 1.7,
            'plus_minus': 0.7
        }
    }
}

def get_player_stats(player_name: str) -> Optional[Dict]:
    """Get stats for a specific player with caching"""
    try:
        # Check cache first
        if player_name in _player_stats_cache:
            return _player_stats_cache[player_name]
            
        # Get from static player pool
        player_pool = get_static_player_pool()
        for cost_tier in player_pool.values():
            for player in cost_tier:
                if player['name'].lower() == player_name.lower():
                    _player_stats_cache[player_name] = player
                    return player
                    
        logger.warning(f"Player {player_name} not found in static pool")
        return None
        
    except Exception as e:
        logger.error(f"Error getting stats for {player_name}: {str(e)}")
        return None

def get_all_player_stats() -> List[Dict]:
    """Get stats for all players"""
    try:
        player_pool = get_static_player_pool()
        all_players = []
        for cost_tier in player_pool.values():
            all_players.extend(cost_tier)
        return all_players
    except Exception as e:
        logger.error(f"Error getting all player stats: {str(e)}")
        return []

def get_player_3_season_avg(player_name: str) -> dict:
    """Get 3-season average stats for a specific player"""
    player = PLAYER_STATS.get(player_name, {})
    return player.get('3_season_avg', {}) if player else {}

def get_all_player_3_season_avg() -> dict:
    """Get 3-season average stats for all players"""
    return {name: data['3_season_avg'] for name, data in PLAYER_STATS.items()}

def clear_cache():
    """Clear the player stats cache"""
    global _player_stats_cache
    _player_stats_cache.clear() 