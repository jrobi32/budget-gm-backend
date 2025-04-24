"""
Static player pool containing all NBA players with their stats.
This file contains the complete list of players categorized by cost tier.
"""

PLAYER_POOL = {
    '$1': [
        {
            'name': 'T.J. McConnell',
            'position': 'PG',
            'team': 'IND',
            'cost': '$1',
            'rating': 75,
            'stats': {
                'pts': 8.5,
                'ast': 5.3,
                'reb': 2.7,
                'stl': 1.0,
                'blk': 0.1,
                'fg_pct': 54.6,
                'ts_pct': 58.2,
                'gp': 76,
                '3pt_pct': 44.1,
                'ft_pct': 78.9,
                'tov': 1.3,
                'plus_minus': 2.1
            },
            '3_season_avg': {
                'pts': 8.1,
                'ast': 5.1,
                'reb': 2.5,
                'stl': 0.9,
                'blk': 0.1,
                'fg_pct': 54.2,
                'ts_pct': 57.8,
                'gp': 74,
                '3pt_pct': 43.8,
                'ft_pct': 78.5,
                'tov': 1.2,
                'plus_minus': 1.9
            }
        },
        {
            'name': 'Jae Crowder',
            'position': 'PF',
            'team': 'MIL',
            'cost': '$1',
            'rating': 74,
            'stats': {
                'pts': 6.9,
                'ast': 1.9,
                'reb': 3.8,
                'stl': 0.7,
                'blk': 0.3,
                'fg_pct': 41.5,
                'ts_pct': 55.2,
                'gp': 78,
                '3pt_pct': 35.1,
                'ft_pct': 78.3,
                'tov': 0.8,
                'plus_minus': 1.5
            },
            '3_season_avg': {
                'pts': 6.5,
                'ast': 1.8,
                'reb': 3.6,
                'stl': 0.7,
                'blk': 0.3,
                'fg_pct': 41.1,
                'ts_pct': 54.8,
                'gp': 76,
                '3pt_pct': 34.8,
                'ft_pct': 77.9,
                'tov': 0.8,
                'plus_minus': 1.3
            }
        },
        {
            'name': 'Pat Connaughton',
            'position': 'SG',
            'team': 'MIL',
            'cost': '$1',
            'rating': 73,
            'stats': {
                'pts': 7.6,
                'ast': 1.3,
                'reb': 3.8,
                'stl': 0.5,
                'blk': 0.2,
                'fg_pct': 45.2,
                'ts_pct': 58.7,
                'gp': 65,
                '3pt_pct': 39.5,
                'ft_pct': 81.2,
                'tov': 0.6,
                'plus_minus': 1.8
            },
            '3_season_avg': {
                'pts': 7.2,
                'ast': 1.2,
                'reb': 3.6,
                'stl': 0.5,
                'blk': 0.2,
                'fg_pct': 44.8,
                'ts_pct': 58.3,
                'gp': 63,
                '3pt_pct': 39.2,
                'ft_pct': 80.8,
                'tov': 0.6,
                'plus_minus': 1.6
            }
        },
        {
            'name': 'Dario Saric',
            'position': 'PF',
            'team': 'GSW',
            'cost': '$1',
            'rating': 72,
            'stats': {
                'pts': 6.4,
                'ast': 1.3,
                'reb': 3.6,
                'stl': 0.4,
                'blk': 0.1,
                'fg_pct': 47.9,
                'ts_pct': 58.1,
                'gp': 57,
                '3pt_pct': 39.1,
                'ft_pct': 78.5,
                'tov': 0.9,
                'plus_minus': 1.2
            },
            '3_season_avg': {
                'pts': 6.0,
                'ast': 1.2,
                'reb': 3.4,
                'stl': 0.4,
                'blk': 0.1,
                'fg_pct': 47.5,
                'ts_pct': 57.7,
                'gp': 55,
                '3pt_pct': 38.8,
                'ft_pct': 78.1,
                'tov': 0.8,
                'plus_minus': 1.0
            }
        },
        {
            'name': 'Jevon Carter',
            'position': 'PG',
            'team': 'CHI',
            'cost': '$1',
            'rating': 71,
            'stats': {
                'pts': 6.6,
                'ast': 1.7,
                'reb': 1.7,
                'stl': 0.8,
                'blk': 0.2,
                'fg_pct': 42.1,
                'ts_pct': 55.8,
                'gp': 81,
                '3pt_pct': 36.7,
                'ft_pct': 80.0,
                'tov': 0.7,
                'plus_minus': 1.0
            },
            '3_season_avg': {
                'pts': 6.2,
                'ast': 1.6,
                'reb': 1.6,
                'stl': 0.7,
                'blk': 0.2,
                'fg_pct': 41.7,
                'ts_pct': 55.4,
                'gp': 79,
                '3pt_pct': 36.4,
                'ft_pct': 79.6,
                'tov': 0.7,
                'plus_minus': 0.8
            }
        },
        {
            'name': 'Drew Eubanks',
            'position': 'C',
            'team': 'PHX',
            'cost': '$1',
            'rating': 70,
            'stats': {
                'pts': 6.6,
                'ast': 1.1,
                'reb': 4.3,
                'stl': 0.4,
                'blk': 0.8,
                'fg_pct': 64.0,
                'ts_pct': 65.2,
                'gp': 78,
                '3pt_pct': 0.0,
                'ft_pct': 70.8,
                'tov': 0.8,
                'plus_minus': 0.5
            },
            '3_season_avg': {
                'pts': 6.2,
                'ast': 1.0,
                'reb': 4.1,
                'stl': 0.4,
                'blk': 0.7,
                'fg_pct': 63.6,
                'ts_pct': 64.8,
                'gp': 76,
                '3pt_pct': 0.0,
                'ft_pct': 70.4,
                'tov': 0.7,
                'plus_minus': 0.3
            }
        },
        {
            'name': 'Cedi Osman',
            'position': 'SF',
            'team': 'SAS',
            'cost': '$1',
            'rating': 69,
            'stats': {
                'pts': 8.7,
                'ast': 1.5,
                'reb': 2.3,
                'stl': 0.5,
                'blk': 0.1,
                'fg_pct': 45.7,
                'ts_pct': 56.3,
                'gp': 77,
                '3pt_pct': 37.2,
                'ft_pct': 75.6,
                'tov': 1.0,
                'plus_minus': -0.8
            },
            '3_season_avg': {
                'pts': 8.3,
                'ast': 1.4,
                'reb': 2.2,
                'stl': 0.5,
                'blk': 0.1,
                'fg_pct': 45.3,
                'ts_pct': 55.9,
                'gp': 75,
                '3pt_pct': 36.9,
                'ft_pct': 75.2,
                'tov': 0.9,
                'plus_minus': -1.0
            }
        },
        {
            'name': 'Josh Okogie',
            'position': 'SG',
            'team': 'PHX',
            'cost': '$1',
            'rating': 68,
            'stats': {
                'pts': 7.3,
                'ast': 1.5,
                'reb': 3.5,
                'stl': 0.8,
                'blk': 0.5,
                'fg_pct': 42.9,
                'ts_pct': 54.8,
                'gp': 72,
                '3pt_pct': 33.5,
                'ft_pct': 76.2,
                'tov': 0.9,
                'plus_minus': -1.2
            },
            '3_season_avg': {
                'pts': 6.9,
                'ast': 1.4,
                'reb': 3.3,
                'stl': 0.7,
                'blk': 0.4,
                'fg_pct': 42.5,
                'ts_pct': 54.4,
                'gp': 70,
                '3pt_pct': 33.2,
                'ft_pct': 75.8,
                'tov': 0.8,
                'plus_minus': -1.4
            }
        },
        {
            'name': 'Jalen McDaniels',
            'position': 'PF',
            'team': 'TOR',
            'cost': '$1',
            'rating': 67,
            'stats': {
                'pts': 6.2,
                'ast': 1.1,
                'reb': 3.2,
                'stl': 0.6,
                'blk': 0.4,
                'fg_pct': 44.8,
                'ts_pct': 53.9,
                'gp': 68,
                '3pt_pct': 32.7,
                'ft_pct': 73.5,
                'tov': 0.7,
                'plus_minus': -1.5
            },
            '3_season_avg': {
                'pts': 5.8,
                'ast': 1.0,
                'reb': 3.0,
                'stl': 0.6,
                'blk': 0.3,
                'fg_pct': 44.4,
                'ts_pct': 53.5,
                'gp': 66,
                '3pt_pct': 32.4,
                'ft_pct': 73.1,
                'tov': 0.6,
                'plus_minus': -1.7
            }
        }
    ],
    '$5': [
        {
            'name': 'Jayson Tatum',
            'position': 'SF',
            'team': 'BOS',
            'cost': '$5',
            'rating': 95,
            'stats': {
                'pts': 30.1,
                'ast': 4.6,
                'reb': 8.8,
                'stl': 1.1,
                'blk': 0.7,
                'fg_pct': 46.6,
                'ts_pct': 60.5,
                'gp': 74,
                '3pt_pct': 35.0,
                'ft_pct': 85.4,
                'tov': 2.9,
                'plus_minus': 6.8
            },
            '3_season_avg': {
                'pts': 28.5,
                'ast': 4.3,
                'reb': 8.1,
                'stl': 1.0,
                'blk': 0.6,
                'fg_pct': 45.8,
                'ts_pct': 59.8,
                'gp': 72,
                '3pt_pct': 34.5,
                'ft_pct': 84.9,
                'tov': 2.7,
                'plus_minus': 6.2
            }
        },
        {
            'name': 'Devin Booker',
            'position': 'SG',
            'team': 'PHX',
            'cost': '$5',
            'rating': 94,
            'stats': {
                'pts': 27.8,
                'ast': 5.5,
                'reb': 4.5,
                'stl': 1.0,
                'blk': 0.3,
                'fg_pct': 49.4,
                'ts_pct': 61.8,
                'gp': 68,
                '3pt_pct': 35.1,
                'ft_pct': 85.6,
                'tov': 3.2,
                'plus_minus': 5.4
            },
            '3_season_avg': {
                'pts': 26.8,
                'ast': 5.2,
                'reb': 4.3,
                'stl': 0.9,
                'blk': 0.3,
                'fg_pct': 48.9,
                'ts_pct': 61.2,
                'gp': 66,
                '3pt_pct': 34.8,
                'ft_pct': 85.2,
                'tov': 3.0,
                'plus_minus': 5.1
            }
        },
        {
            'name': 'Stephen Curry',
            'position': 'PG',
            'team': 'GSW',
            'cost': '$5',
            'rating': 93,
            'stats': {
                'pts': 26.4,
                'ast': 6.1,
                'reb': 4.5,
                'stl': 0.9,
                'blk': 0.4,
                'fg_pct': 47.3,
                'ts_pct': 65.6,
                'gp': 56,
                '3pt_pct': 42.7,
                'ft_pct': 91.5,
                'tov': 3.2,
                'plus_minus': 6.2
            },
            '3_season_avg': {
                'pts': 25.8,
                'ast': 6.0,
                'reb': 4.4,
                'stl': 0.9,
                'blk': 0.3,
                'fg_pct': 46.9,
                'ts_pct': 65.2,
                'gp': 54,
                '3pt_pct': 42.3,
                'ft_pct': 91.2,
                'tov': 3.1,
                'plus_minus': 6.0
            }
        },
        {
            'name': 'Luka Doncic',
            'position': 'PG',
            'team': 'DAL',
            'cost': '$5',
            'rating': 95,
            'stats': {
                'pts': 32.4,
                'ast': 8.0,
                'reb': 8.6,
                'stl': 1.4,
                'blk': 0.5,
                'fg_pct': 49.6,
                'ts_pct': 61.0,
                'gp': 66,
                '3pt_pct': 34.2,
                'ft_pct': 74.2,
                'tov': 3.6,
                'plus_minus': 5.8
            },
            '3_season_avg': {
                'pts': 31.2,
                'ast': 7.8,
                'reb': 8.4,
                'stl': 1.3,
                'blk': 0.4,
                'fg_pct': 49.1,
                'ts_pct': 60.5,
                'gp': 64,
                '3pt_pct': 33.9,
                'ft_pct': 73.8,
                'tov': 3.5,
                'plus_minus': 5.5
            }
        },
        {
            'name': 'Giannis Antetokounmpo',
            'position': 'PF',
            'team': 'MIL',
            'cost': '$5',
            'rating': 96,
            'stats': {
                'pts': 31.1,
                'ast': 5.7,
                'reb': 11.8,
                'stl': 0.8,
                'blk': 0.8,
                'fg_pct': 55.3,
                'ts_pct': 60.5,
                'gp': 63,
                '3pt_pct': 27.5,
                'ft_pct': 64.5,
                'tov': 3.3,
                'plus_minus': 7.2
            },
            '3_season_avg': {
                'pts': 30.5,
                'ast': 5.6,
                'reb': 11.5,
                'stl': 0.8,
                'blk': 0.8,
                'fg_pct': 54.9,
                'ts_pct': 60.0,
                'gp': 61,
                '3pt_pct': 27.2,
                'ft_pct': 64.2,
                'tov': 3.2,
                'plus_minus': 7.0
            }
        },
        {
            'name': 'Nikola Jokic',
            'position': 'C',
            'team': 'DEN',
            'cost': '$5',
            'rating': 97,
            'stats': {
                'pts': 24.5,
                'ast': 9.8,
                'reb': 11.8,
                'stl': 1.3,
                'blk': 0.7,
                'fg_pct': 63.2,
                'ts_pct': 70.1,
                'gp': 69,
                '3pt_pct': 38.3,
                'ft_pct': 82.2,
                'tov': 3.6,
                'plus_minus': 8.4
            },
            '3_season_avg': {
                'pts': 24.0,
                'ast': 9.6,
                'reb': 11.5,
                'stl': 1.2,
                'blk': 0.7,
                'fg_pct': 62.8,
                'ts_pct': 69.8,
                'gp': 67,
                '3pt_pct': 38.0,
                'ft_pct': 81.9,
                'tov': 3.5,
                'plus_minus': 8.2
            }
        },
        {
            'name': 'Joel Embiid',
            'position': 'C',
            'team': 'PHI',
            'cost': '$5',
            'rating': 96,
            'stats': {
                'pts': 33.1,
                'ast': 4.2,
                'reb': 10.2,
                'stl': 1.0,
                'blk': 1.7,
                'fg_pct': 54.8,
                'ts_pct': 65.5,
                'gp': 66,
                '3pt_pct': 33.0,
                'ft_pct': 85.7,
                'tov': 3.4,
                'plus_minus': 7.8
            },
            '3_season_avg': {
                'pts': 32.5,
                'ast': 4.1,
                'reb': 10.0,
                'stl': 1.0,
                'blk': 1.6,
                'fg_pct': 54.4,
                'ts_pct': 65.2,
                'gp': 64,
                '3pt_pct': 32.8,
                'ft_pct': 85.4,
                'tov': 3.3,
                'plus_minus': 7.6
            }
        },
        {
            'name': 'Kevin Durant',
            'position': 'SF',
            'team': 'PHX',
            'cost': '$5',
            'rating': 94,
            'stats': {
                'pts': 29.1,
                'ast': 5.0,
                'reb': 6.7,
                'stl': 0.5,
                'blk': 1.4,
                'fg_pct': 56.0,
                'ts_pct': 67.7,
                'gp': 47,
                '3pt_pct': 40.4,
                'ft_pct': 91.9,
                'tov': 3.3,
                'plus_minus': 6.5
            },
            '3_season_avg': {
                'pts': 28.5,
                'ast': 4.9,
                'reb': 6.5,
                'stl': 0.5,
                'blk': 1.3,
                'fg_pct': 55.6,
                'ts_pct': 67.4,
                'gp': 45,
                '3pt_pct': 40.1,
                'ft_pct': 91.6,
                'tov': 3.2,
                'plus_minus': 6.3
            }
        },
        {
            'name': 'LeBron James',
            'position': 'SF',
            'team': 'LAL',
            'cost': '$5',
            'rating': 93,
            'stats': {
                'pts': 28.9,
                'ast': 6.8,
                'reb': 8.3,
                'stl': 0.9,
                'blk': 0.6,
                'fg_pct': 50.0,
                'ts_pct': 58.3,
                'gp': 55,
                '3pt_pct': 32.1,
                'ft_pct': 76.8,
                'tov': 3.4,
                'plus_minus': 5.2
            },
            '3_season_avg': {
                'pts': 28.3,
                'ast': 6.6,
                'reb': 8.1,
                'stl': 0.9,
                'blk': 0.6,
                'fg_pct': 49.6,
                'ts_pct': 58.0,
                'gp': 53,
                '3pt_pct': 31.9,
                'ft_pct': 76.5,
                'tov': 3.3,
                'plus_minus': 5.0
            }
        },
        {
            'name': 'Ja Morant',
            'position': 'PG',
            'team': 'MEM',
            'cost': '$5',
            'rating': 92,
            'stats': {
                'pts': 26.2,
                'ast': 8.1,
                'reb': 5.9,
                'stl': 1.1,
                'blk': 0.3,
                'fg_pct': 46.6,
                'ts_pct': 55.7,
                'gp': 61,
                '3pt_pct': 30.7,
                'ft_pct': 74.8,
                'tov': 3.4,
                'plus_minus': 4.8
            },
            '3_season_avg': {
                'pts': 25.8,
                'ast': 7.9,
                'reb': 5.7,
                'stl': 1.0,
                'blk': 0.3,
                'fg_pct': 46.2,
                'ts_pct': 55.4,
                'gp': 59,
                '3pt_pct': 30.4,
                'ft_pct': 74.5,
                'tov': 3.3,
                'plus_minus': 4.6
            }
        }
    ]
}

def get_static_player_pool() -> dict:
    """Get the static player pool"""
    return PLAYER_POOL

def get_players_by_cost(cost: str) -> list:
    """Get players by cost tier"""
    return PLAYER_POOL.get(cost, [])

def get_all_players() -> list:
    """Get all players as a flat list"""
    all_players = []
    for cost_tier in PLAYER_POOL.values():
        all_players.extend(cost_tier)
    return all_players