from data_fetcher import NBADataFetcher
import json
import logging
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_player_rating(row):
    """Calculate player rating based on stats"""
    # Basic stats weights
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
        if stat in ['FG_PCT', 'TS_PCT']:
            rating += float(row[stat]) * weight * 100
        else:
            rating += float(row[stat]) * weight
    
    # Add bonuses for exceptional performance
    if row['PTS'] >= 25: rating += 10  # Bonus for high scorers
    if row['AST'] >= 8: rating += 8    # Bonus for playmakers
    if row['REB'] >= 10: rating += 8   # Bonus for rebounders
    if row['STL'] >= 2: rating += 5    # Bonus for defenders
    if row['BLK'] >= 2: rating += 5    # Bonus for rim protectors
    
    return rating

def main():
    fetcher = NBADataFetcher()
    
    # Get player stats DataFrame
    df = fetcher.get_player_stats()
    
    if df.empty:
        logger.error("No player stats available")
        return
    
    # Calculate player ratings
    df['rating'] = df.apply(calculate_player_rating, axis=1)
    
    # Normalize ratings to 1-100 range
    min_rating = df['rating'].min()
    max_rating = df['rating'].max()
    df['rating'] = ((df['rating'] - min_rating) / (max_rating - min_rating)) * 99 + 1
    
    # Calculate percentiles for ratings
    df['percentile'] = df['rating'].rank(pct=True) * 100
    
    # Assign costs based on percentiles
    def get_cost(percentile):
        if percentile >= 94:    # Top 6%
            return '$5'
        elif percentile >= 85:  # Next 9%
            return '$4'
        elif percentile >= 70:  # Next 15%
            return '$3'
        elif percentile >= 50:  # Next 20%
            return '$2'
        else:                   # Bottom 50%
            return '$1'
    
    df['cost'] = df['percentile'].apply(get_cost)
    
    # Initialize cost distribution counter
    cost_distribution = {'$5': 0, '$4': 0, '$3': 0, '$2': 0, '$1': 0}
    player_pool = []
    
    # Process each player
    for _, row in df.iterrows():
        if row['GP'] > 0:  # Only include players who have played games
            player_data = {
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
            cost_distribution[player_data['cost']] += 1
            player_pool.append(player_data)
    
    # Log cost distribution
    logger.info("Cost distribution:")
    for cost, count in cost_distribution.items():
        logger.info(f"{cost}: {count} players")
    
    # Save to JSON file
    output = {
        'last_updated': datetime.now().isoformat(),
        'players': player_pool
    }
    
    with open('player_pool.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"Successfully saved {len(player_pool)} players to player_pool.json")

if __name__ == '__main__':
    main() 