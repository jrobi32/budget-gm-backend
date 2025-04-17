import json
import random

# Original NBA stars for each category
PLAYER_POOL = {
    '$3': [
        {'id': 203507, 'name': 'Giannis Antetokounmpo', 'stats': {'games_played': 67.7, 'points': 30.6, 'rebounds': 11.7, 'assists': 6.2, 'steals': 1.0, 'blocks': 1.0, 'fg_pct': 0.59, 'ft_pct': 0.61, 'three_pct': 0.20, 'minutes': 33.9}},
        {'id': 1628983, 'name': 'Shai Gilgeous-Alexander', 'stats': {'games_played': 73.0, 'points': 31.4, 'rebounds': 5.1, 'assists': 6.0, 'steals': 1.8, 'blocks': 1.0, 'fg_pct': 0.52, 'ft_pct': 0.89, 'three_pct': 0.37, 'minutes': 34.6}},
        {'id': 203999, 'name': 'Nikola Jokić', 'stats': {'games_played': 72.7, 'points': 26.8, 'rebounds': 12.3, 'assists': 9.7, 'steals': 1.5, 'blocks': 0.7, 'fg_pct': 0.61, 'ft_pct': 0.77, 'three_pct': 0.36, 'minutes': 35.0}},
        {'id': 1628369, 'name': 'Jayson Tatum', 'stats': {'games_played': 73.3, 'points': 27.9, 'rebounds': 8.5, 'assists': 5.2, 'steals': 1.0, 'blocks': 0.6, 'fg_pct': 0.46, 'ft_pct': 0.82, 'three_pct': 0.35, 'minutes': 36.4}},
        {'id': 1630162, 'name': 'Anthony Edwards', 'stats': {'games_played': 79.0, 'points': 26.0, 'rebounds': 5.6, 'assists': 4.7, 'steals': 1.3, 'blocks': 0.6, 'fg_pct': 0.45, 'ft_pct': 0.76, 'three_pct': 0.37, 'minutes': 35.8}},
        {'id': 201142, 'name': 'Kevin Durant', 'stats': {'games_played': 61.3, 'points': 27.6, 'rebounds': 6.4, 'assists': 4.8, 'steals': 0.8, 'blocks': 1.3, 'fg_pct': 0.54, 'ft_pct': 0.84, 'three_pct': 0.42, 'minutes': 36.5}},
        {'id': 201939, 'name': 'Stephen Curry', 'stats': {'games_played': 66.7, 'points': 26.8, 'rebounds': 5.0, 'assists': 5.8, 'steals': 0.9, 'blocks': 0.4, 'fg_pct': 0.46, 'ft_pct': 0.85, 'three_pct': 0.41, 'minutes': 33.2}},
        {'id': 2544, 'name': 'LeBron James', 'stats': {'games_played': 65.3, 'points': 26.3, 'rebounds': 7.8, 'assists': 7.8, 'steals': 1.1, 'blocks': 0.6, 'fg_pct': 0.52, 'ft_pct': 0.74, 'three_pct': 0.35, 'minutes': 35.3}}
    ],
    '$2': [
        {'id': 203081, 'name': 'Damian Lillard', 'stats': {'games_played': 63.0, 'points': 27.1, 'rebounds': 4.6, 'assists': 7.1, 'steals': 1.0, 'blocks': 0.2, 'fg_pct': 0.44, 'ft_pct': 0.90, 'three_pct': 0.36, 'minutes': 36.0}},
        {'id': 1628973, 'name': 'Jalen Brunson', 'stats': {'games_played': 70.0, 'points': 26.2, 'rebounds': 3.3, 'assists': 6.7, 'steals': 0.9, 'blocks': 0.2, 'fg_pct': 0.48, 'ft_pct': 0.79, 'three_pct': 0.37, 'minutes': 35.3}},
        {'id': 1630595, 'name': 'Cade Cunningham', 'stats': {'games_played': 48.0, 'points': 22.9, 'rebounds': 5.5, 'assists': 7.5, 'steals': 0.9, 'blocks': 0.6, 'fg_pct': 0.44, 'ft_pct': 0.76, 'three_pct': 0.31, 'minutes': 33.9}},
        {'id': 1626164, 'name': 'Devin Booker', 'stats': {'games_played': 65.3, 'points': 26.8, 'rebounds': 4.4, 'assists': 6.5, 'steals': 0.9, 'blocks': 0.3, 'fg_pct': 0.47, 'ft_pct': 0.87, 'three_pct': 0.33, 'minutes': 35.9}},
        {'id': 1628378, 'name': 'Donovan Mitchell', 'stats': {'games_played': 64.7, 'points': 26.3, 'rebounds': 4.6, 'assists': 5.2, 'steals': 1.5, 'blocks': 0.4, 'fg_pct': 0.46, 'ft_pct': 0.80, 'three_pct': 0.36, 'minutes': 34.2}},
        {'id': 1629027, 'name': 'Trae Young', 'stats': {'games_played': 67.7, 'points': 25.4, 'rebounds': 2.9, 'assists': 10.8, 'steals': 1.2, 'blocks': 0.2, 'fg_pct': 0.42, 'ft_pct': 0.85, 'three_pct': 0.34, 'minutes': 35.6}},
        {'id': 1626157, 'name': 'Karl-Anthony Towns', 'stats': {'games_played': 54.3, 'points': 22.3, 'rebounds': 9.7, 'assists': 3.7, 'steals': 0.8, 'blocks': 0.6, 'fg_pct': 0.51, 'ft_pct': 0.80, 'three_pct': 0.41, 'minutes': 33.5}}
    ],
    '$1': [
        {'id': 1630193, 'name': 'Tyrese Maxey', 'stats': {'games_played': 74.0, 'points': 20.3, 'rebounds': 2.9, 'assists': 3.5, 'steals': 0.8, 'blocks': 0.2, 'fg_pct': 0.48, 'ft_pct': 0.85, 'three_pct': 0.43, 'minutes': 33.6}},
        {'id': 1629639, 'name': 'Tyler Herro', 'stats': {'games_played': 62.0, 'points': 21.6, 'rebounds': 5.3, 'assists': 4.7, 'steals': 0.7, 'blocks': 0.2, 'fg_pct': 0.45, 'ft_pct': 0.79, 'three_pct': 0.37, 'minutes': 33.3}},
        {'id': 1630178, 'name': 'LaMelo Ball', 'stats': {'games_played': 58.0, 'points': 23.3, 'rebounds': 6.4, 'assists': 8.4, 'steals': 1.3, 'blocks': 0.3, 'fg_pct': 0.43, 'ft_pct': 0.82, 'three_pct': 0.37, 'minutes': 35.2}},
        {'id': 1630169, 'name': 'Tyrese Haliburton', 'stats': {'games_played': 69.0, 'points': 20.1, 'rebounds': 3.9, 'assists': 10.4, 'steals': 1.2, 'blocks': 0.5, 'fg_pct': 0.47, 'ft_pct': 0.85, 'three_pct': 0.36, 'minutes': 33.6}},
        {'id': 1630168, 'name': 'Jalen Suggs', 'stats': {'games_played': 65.0, 'points': 15.8, 'rebounds': 3.5, 'assists': 4.2, 'steals': 1.2, 'blocks': 0.4, 'fg_pct': 0.43, 'ft_pct': 0.77, 'three_pct': 0.34, 'minutes': 30.5}}
    ],
    '$0': [
        {'id': 1630224, 'name': 'Desmond Bane', 'stats': {'games_played': 58.0, 'points': 19.8, 'rebounds': 4.5, 'assists': 3.8, 'steals': 0.9, 'blocks': 0.3, 'fg_pct': 0.45, 'ft_pct': 0.82, 'three_pct': 0.38, 'minutes': 32.5}},
        {'id': 1630567, 'name': 'Jalen Green', 'stats': {'games_played': 72.0, 'points': 18.5, 'rebounds': 3.2, 'assists': 3.2, 'steals': 0.7, 'blocks': 0.2, 'fg_pct': 0.42, 'ft_pct': 0.78, 'three_pct': 0.35, 'minutes': 31.8}},
        {'id': 1630559, 'name': 'Franz Wagner', 'stats': {'games_played': 71.0, 'points': 19.2, 'rebounds': 4.8, 'assists': 3.5, 'steals': 0.8, 'blocks': 0.4, 'fg_pct': 0.46, 'ft_pct': 0.81, 'three_pct': 0.36, 'minutes': 32.9}},
        {'id': 1630530, 'name': 'Josh Giddey', 'stats': {'games_played': 68.0, 'points': 16.5, 'rebounds': 6.2, 'assists': 5.8, 'steals': 0.7, 'blocks': 0.3, 'fg_pct': 0.44, 'ft_pct': 0.75, 'three_pct': 0.33, 'minutes': 31.2}},
        {'id': 1630166, 'name': 'Jalen Suggs', 'stats': {'games_played': 65.0, 'points': 15.8, 'rebounds': 3.5, 'assists': 4.2, 'steals': 1.2, 'blocks': 0.4, 'fg_pct': 0.43, 'ft_pct': 0.77, 'three_pct': 0.34, 'minutes': 30.5}}
    ]
}

if __name__ == '__main__':
    # Save to file
    with open('player_pool.json', 'w') as f:
        json.dump(PLAYER_POOL, f, indent=4)
    
    print("Generated player pool with:")
    for category, players in PLAYER_POOL.items():
        print(f"{category}: {len(players)} players") 