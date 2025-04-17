import json
import requests
import pandas as pd
from typing import Dict, List

def fetch_nba_players():
    """Fetch top 175 players by points per game from NBA API"""
    url = "https://stats.nba.com/stats/leaguedashplayerstats"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.nba.com/'
    }
    params = {
        'College': '',
        'Conference': '',
        'Country': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'DraftPick': '',
        'DraftYear': '',
        'GameScope': '',
        'GameSegment': '',
        'Height': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'MeasureType': 'Base',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'PerGame',
        'Period': '0',
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'Y',
        'Season': '2023-24',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': '0',
        'TwoWay': '0',
        'VsConference': '',
        'VsDivision': '',
        'Weight': ''
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    # Extract player data
    headers = data['resultSets'][0]['headers']
    rows = data['resultSets'][0]['rowSet']
    
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Select relevant columns and rename them
    df = df[['PLAYER_ID', 'PLAYER_NAME', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FT_PCT', 'FG3_PCT', 'GP', 'MIN']]
    df.columns = ['id', 'name', 'points', 'rebounds', 'assists', 'steals', 'blocks', 'fg_pct', 'ft_pct', 'three_pct', 'games_played', 'minutes']
    
    # Sort by points and take top 175
    df = df.sort_values('points', ascending=False).head(175)
    
    return df

def calculate_player_cost(stats: pd.Series) -> int:
    """Calculate player cost based on performance metrics"""
    # Basic stats weights
    weights = {
        'points': 0.45,      # Points (increased weight)
        'assists': 0.20,     # Assists (playmaking)
        'rebounds': 0.15,    # Rebounds
        'steals': 0.10,      # Steals
        'blocks': 0.10,      # Blocks
        'fg_pct': 0.05,      # Field Goal Percentage
        'ft_pct': 0.05       # Free Throw Percentage
    }
    
    # Calculate weighted score
    score = 0
    for stat, weight in weights.items():
        if stat in stats:
            if stat in ['fg_pct', 'ft_pct', 'three_pct']:
                # Convert percentages to 0-1 scale
                score += (stats[stat] / 100) * weight * 10
            else:
                # Scale counting stats appropriately
                score += stats[stat] * weight
    
    # Add bonuses for exceptional performance
    if stats['points'] >= 25:  # Elite scoring
        score += 15
    elif stats['points'] >= 20:  # Very good scoring
        score += 10
    elif stats['points'] >= 15:  # Good scoring
        score += 5
        
    if stats['assists'] >= 7:   # Elite playmaking
        score += 8
    elif stats['assists'] >= 5:  # Very good playmaking
        score += 4
        
    if stats['rebounds'] >= 10:  # Elite rebounding
        score += 8
    elif stats['rebounds'] >= 7:  # Very good rebounding
        score += 4
        
    if stats['steals'] + stats['blocks'] >= 2.5:  # Elite defense
        score += 8
    elif stats['steals'] + stats['blocks'] >= 1.5:  # Very good defense
        score += 4
        
    if stats['fg_pct'] >= 0.50:  # Elite efficiency
        score += 4
        
    # Apply games played adjustment
    games_played_percentage = min(stats['games_played'] / 82, 1.0)  # Cap at 100%
    
    # Apply a minimum threshold - players with less than 50% of games get penalized more
    if games_played_percentage < 0.5:
        score *= (games_played_percentage * 0.7)  # 70% of their games played percentage
    else:
        score *= (0.5 + (games_played_percentage - 0.5) * 0.8)  # Scale from 50% to 90%
    
    # Normalize score to 0-3 range
    if score > 25:
        return 3
    elif score > 18:
        return 2
    elif score > 12:
        return 1
    else:
        return 0

def main():
    # Fetch player data
    print("Fetching NBA player data...")
    players_df = fetch_nba_players()
    
    # Initialize categorized players
    categorized_players = {
        '$3': [],  # Elite players
        '$2': [],  # Very good players
        '$1': [],  # Solid players
        '$0': []   # Role players
    }
    
    # Process each player
    for _, player in players_df.iterrows():
        cost = calculate_player_cost(player)
        player_data = {
            'id': int(player['id']),
            'name': player['name'],
            'stats': {
                'games_played': float(player['games_played']),
                'points': float(player['points']),
                'rebounds': float(player['rebounds']),
                'assists': float(player['assists']),
                'steals': float(player['steals']),
                'blocks': float(player['blocks']),
                'fg_pct': float(player['fg_pct']),
                'ft_pct': float(player['ft_pct']),
                'three_pct': float(player['three_pct']),
                'minutes': float(player['minutes'])
            }
        }
        categorized_players[f'${cost}'].append(player_data)
    
    # Save to file
    with open('player_pool.json', 'w') as f:
        json.dump(categorized_players, f, indent=4)
    
    print("\nGenerated player pool with:")
    for category, players in categorized_players.items():
        print(f"{category}: {len(players)} players")

if __name__ == '__main__':
    main() 