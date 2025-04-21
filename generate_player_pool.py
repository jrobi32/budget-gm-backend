import json
import requests
import pandas as pd
import random
from typing import Dict, List

def fetch_nba_players():
    """Fetch top 350 players by points per game from NBA API"""
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
    
    # Sort by points and take top 350
    df = df.sort_values('points', ascending=False).head(350)
    
    return df

def calculate_player_cost(stats: pd.Series) -> int:
    """Calculate player cost based on performance metrics"""
    # Basic stats weights
    weights = {
        'points': 0.40,      # Points (major factor)
        'assists': 0.25,     # Assists (playmaking)
        'rebounds': 0.20,    # Rebounds
        'steals': 0.05,      # Steals
        'blocks': 0.05,      # Blocks
        'fg_pct': 0.05,      # Field Goal Percentage
        'ts_pct': 0.05       # True Shooting Percentage
    }
    
    # Calculate weighted score
    score = 0
    for stat, weight in weights.items():
        if stat in stats:
            if stat in ['fg_pct', 'ts_pct']:
                # Convert percentages to 0-1 scale
                score += (stats[stat] / 100) * weight * 10
            else:
                # Scale counting stats appropriately
                score += stats[stat] * weight
    
    # Add bonuses for exceptional performance
    if stats['points'] >= 30:  # MVP-level scoring
        score += 20
    elif stats['points'] >= 25:  # All-Star level scoring
        score += 15
    elif stats['points'] >= 20:  # High-end starter scoring
        score += 10
    elif stats['points'] >= 15:  # Solid starter scoring
        score += 5
        
    if stats['assists'] >= 10:   # Elite playmaking
        score += 15
    elif stats['assists'] >= 7:  # All-Star playmaking
        score += 10
    elif stats['assists'] >= 5:  # Good playmaking
        score += 5
        
    if stats['rebounds'] >= 12:  # Elite rebounding
        score += 15
    elif stats['rebounds'] >= 10:  # All-Star rebounding
        score += 10
    elif stats['rebounds'] >= 7:  # Good rebounding
        score += 5
        
    if stats['steals'] + stats['blocks'] >= 3.0:  # Elite defense
        score += 10
    elif stats['steals'] + stats['blocks'] >= 2.0:  # Very good defense
        score += 5
        
    if stats['ts_pct'] >= 0.65:  # Elite efficiency
        score += 10
    elif stats['ts_pct'] >= 0.60:  # Very good efficiency
        score += 5
        
    # Apply games played adjustment
    games_played_percentage = min(stats['games_played'] / 246, 1.0)  # Cap at 100%
    
    if games_played_percentage < 0.5:
        score *= (games_played_percentage * 0.7)
    else:
        score *= (0.5 + (games_played_percentage - 0.5) * 0.8)
    
    # Normalize score to 1-5 range with new thresholds:
    # $5: Superstars (score > 50)
    # $4: All-Stars (score > 40)
    # $3: Quality starters (score > 30)
    # $2: Solid role players (score > 20)
    # $1: Role players (score <= 20)
    
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

def select_random_players(categorized_players: Dict) -> Dict:
    """Randomly select 5 players from each category"""
    selected_players = {
        '$5': [],
        '$4': [],
        '$3': [],
        '$2': [],
        '$1': []
    }
    
    for category in selected_players:
        # Get all players in this category
        available_players = categorized_players[category]
        
        # If we have more than 5 players, randomly select 5
        if len(available_players) > 5:
            selected = random.sample(available_players, 5)
        else:
            # If we have 5 or fewer, take all of them
            selected = available_players
        
        selected_players[category] = selected
    
    return selected_players

def main():
    # Fetch player data
    print("Fetching NBA player data...")
    players_df = fetch_nba_players()
    
    # Initialize categorized players
    categorized_players = {
        '$5': [],  # Superstars
        '$4': [],  # All-Stars
        '$3': [],  # Quality starters
        '$2': [],  # Solid role players
        '$1': []   # Role players
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
    
    # Sort players in each category by points and assists
    for category in categorized_players:
        categorized_players[category].sort(
            key=lambda x: (x['stats']['points'], x['stats']['assists']),
            reverse=True
        )
    
    # Print total players in each category before selection
    print("\nTotal players in each category:")
    for category, players in categorized_players.items():
        print(f"{category}: {len(players)} players")
    
    # Save full player pool to a separate file for reference
    with open('full_player_pool.json', 'w') as f:
        json.dump(categorized_players, f, indent=4)
    print("\nFull player pool saved to full_player_pool.json")
    
    # Select random players from each category for the game
    selected_players = select_random_players(categorized_players)
    
    # Save selected players to the main player pool file
    with open('player_pool.json', 'w') as f:
        json.dump(selected_players, f, indent=4)
    
    print("\nGenerated game player pool with:")
    for category, players in selected_players.items():
        print(f"{category}: {len(players)} players")

if __name__ == '__main__':
    main() 