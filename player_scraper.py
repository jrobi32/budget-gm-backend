import nba_api.stats.static.players as nba_players
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import commonplayerinfo
import time
import json

def get_player_stats(player_id):
    """Get detailed stats for a specific player"""
    try:
        # Get career stats
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_stats_df = career_stats.get_data_frames()[0]
        
        # Get player info
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        player_info_df = player_info.get_data_frames()[0]
        
        # Get the most recent season's stats
        if not career_stats_df.empty:
            recent_stats = career_stats_df.iloc[-1]
            
            # Calculate player rating based on stats (simplified version)
            rating = calculate_player_rating(recent_stats)
            
            # Create stats dictionary with safe value access
            stats_dict = {
                'pts': safe_float(recent_stats, 'PTS'),
                'ast': safe_float(recent_stats, 'AST'),
                'reb': safe_float(recent_stats, 'REB'),
                'stl': safe_float(recent_stats, 'STL'),
                'blk': safe_float(recent_stats, 'BLK'),
                'fg_pct': safe_float(recent_stats, 'FG_PCT') * 100,
                'ts_pct': calculate_ts_pct(recent_stats),
                'gp': int(safe_float(recent_stats, 'GP')),
                '3pt_pct': safe_float(recent_stats, 'FG3_PCT') * 100,
                'ft_pct': safe_float(recent_stats, 'FT_PCT') * 100,
                'tov': safe_float(recent_stats, 'TOV')
            }
            
            return {
                'name': player_info_df['DISPLAY_FIRST_LAST'].iloc[0],
                'position': player_info_df['POSITION'].iloc[0],
                'team': player_info_df['TEAM_ABBREVIATION'].iloc[0],
                'rating': rating,
                'stats': stats_dict,
                '3_season_avg': calculate_3_season_avg(career_stats_df)
            }
    except Exception as e:
        print(f"Error getting stats for player {player_id}: {str(e)}")
        return None

def safe_float(stats, key):
    """Safely get a float value from stats, return 0.0 if not found or invalid"""
    try:
        return float(stats[key])
    except (KeyError, ValueError, TypeError):
        return 0.0

def calculate_player_rating(stats):
    """Calculate a player rating based on their stats"""
    try:
        rating = (
            safe_float(stats, 'PTS') * 0.35 +  # Increased weight for scoring
            safe_float(stats, 'AST') * 0.15 +
            safe_float(stats, 'REB') * 0.15 +
            safe_float(stats, 'STL') * 0.1 +
            safe_float(stats, 'BLK') * 0.1 +
            (safe_float(stats, 'FG_PCT') * 100) * 0.075 +  # Efficiency metrics
            (safe_float(stats, 'FG3_PCT') * 100) * 0.075
        )
        return round(rating, 1)
    except Exception as e:
        print(f"Error calculating rating: {str(e)}")
        return 0.0

def calculate_ts_pct(stats):
    """Calculate true shooting percentage"""
    try:
        fga = safe_float(stats, 'FGA')
        fta = safe_float(stats, 'FTA')
        pts = safe_float(stats, 'PTS')
        
        if fga == 0 and fta == 0:
            return 0.0
        ts_pct = pts / (2 * (fga + 0.44 * fta))
        return round(ts_pct * 100, 1)
    except:
        return 0.0

def calculate_3_season_avg(career_stats):
    """Calculate 3-season average for a player"""
    if len(career_stats) < 1:  # Changed to require at least 1 season
        return None
    
    try:
        # Take up to 3 most recent seasons
        recent_seasons = career_stats.tail(min(3, len(career_stats)))
        
        # Only use numeric columns for the mean calculation
        numeric_cols = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'FG_PCT', 'GP', 'FG3_PCT', 'FT_PCT', 'TOV']
        stats_mean = recent_seasons[numeric_cols].astype(float).mean()
        
        return {
            'pts': round(float(stats_mean['PTS']), 1),
            'ast': round(float(stats_mean['AST']), 1),
            'reb': round(float(stats_mean['REB']), 1),
            'stl': round(float(stats_mean['STL']), 1),
            'blk': round(float(stats_mean['BLK']), 1),
            'fg_pct': round(float(stats_mean['FG_PCT']) * 100, 1),
            'ts_pct': calculate_ts_pct(stats_mean),
            'gp': round(float(stats_mean['GP'])),
            '3pt_pct': round(float(stats_mean['FG3_PCT']) * 100, 1),
            'ft_pct': round(float(stats_mean['FT_PCT']) * 100, 1),
            'tov': round(float(stats_mean['TOV']), 1)
        }
    except Exception as e:
        print(f"Error calculating 3-season average: {str(e)}")
        return None

def main():
    # Get all active NBA players
    active_players = nba_players.get_active_players()
    
    player_pool = []
    start_processing = False
    
    print(f"Found {len(active_players)} active players")
    
    for player in active_players:
        # Start processing after Domantas Sabonis
        if not start_processing:
            if player['full_name'] == 'Domantas Sabonis':
                start_processing = True
                continue
        
        if start_processing:
            print(f"Processing {player['full_name']}...")
            player_stats = get_player_stats(player['id'])
            
            if player_stats:
                # Remove the cost field since we'll calculate that later
                if 'cost' in player_stats:
                    del player_stats['cost']
                player_pool.append(player_stats)
            
            # Add delay to avoid rate limiting
            time.sleep(0.6)
    
    # Save the player pool to a file
    with open('raw_player_pool_part3.json', 'w') as f:
        json.dump(player_pool, f, indent=4)
    
    print(f"Saved {len(player_pool)} players to raw_player_pool_part3.json")

if __name__ == "__main__":
    main() 