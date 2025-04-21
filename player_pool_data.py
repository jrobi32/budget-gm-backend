def calculate_player_cost(stats):
    """Calculate player cost based on weighted stats"""
    # Weights for different stats
    weights = {
        'points': 0.40,          # Points (major factor)
        'rebounds': 0.20,        # Rebounds
        'assists': 0.25,         # Assists (playmaking)
        'steals': 0.05,          # Steals
        'blocks': 0.05,          # Blocks
        'fg_pct': 0.05,          # Field Goal Percentage
        'ts_pct': 0.05           # True Shooting Percentage
    }
    
    # Calculate weighted value
    weighted_value = 0
    for stat, weight in weights.items():
        if stat in stats:
            # Special handling for percentages
            if stat in ['fg_pct', 'ts_pct']:
                weighted_value += (stats[stat] * 100) * weight  # Convert to percentage
            else:
                weighted_value += stats[stat] * weight
    
    # Add bonuses for exceptional performance
    if stats['points'] >= 30:  # MVP-level scoring
        weighted_value += 20
    elif stats['points'] >= 25:  # All-Star level scoring
        weighted_value += 15
    elif stats['points'] >= 20:  # High-end starter scoring
        weighted_value += 10
    elif stats['points'] >= 15:  # Solid starter scoring
        weighted_value += 5
        
    if stats['assists'] >= 10:   # Elite playmaking
        weighted_value += 15
    elif stats['assists'] >= 7:  # All-Star playmaking
        weighted_value += 10
    elif stats['assists'] >= 5:  # Good playmaking
        weighted_value += 5
        
    if stats['rebounds'] >= 12:  # Elite rebounding
        weighted_value += 15
    elif stats['rebounds'] >= 10:  # All-Star rebounding
        weighted_value += 10
    elif stats['rebounds'] >= 7:  # Good rebounding
        weighted_value += 5
        
    if stats['steals'] + stats['blocks'] >= 3.0:  # Elite defense
        weighted_value += 10
    elif stats['steals'] + stats['blocks'] >= 2.0:  # Very good defense
        weighted_value += 5
        
    if stats['ts_pct'] >= 0.65:  # Elite efficiency
        weighted_value += 10
    elif stats['ts_pct'] >= 0.60:  # Very good efficiency
        weighted_value += 5
    
    # Convert to cost scale (1-5) with new thresholds
    if weighted_value >= 50:      # $5: Superstars
        return 5
    elif weighted_value >= 40:    # $4: All-Stars
        return 4
    elif weighted_value >= 30:    # $3: Quality starters
        return 3
    elif weighted_value >= 20:    # $2: Solid role players
        return 2
    else:                         # $1: Role players
        return 1 