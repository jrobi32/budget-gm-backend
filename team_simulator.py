import json
import pandas as pd
import numpy as np
import random
import math
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from player_stats import get_player_stats, get_player_3_season_avg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, name: str, stats: Dict):
        self.name = name
        self.stats = stats
        self.cost = int(stats.get('cost', '$1').replace('$', ''))  # Use cost from stats
        
    def get_rating(self) -> float:
        """Calculate player rating based on stats"""
        weights = {
            'pts': 1.0,      # Points (major factor)
            'ast': 1.0,      # Assists (playmaking)
            'reb': 0.8,      # Rebounds
            'stl': 0.7,      # Steals
            'blk': 0.7,      # Blocks
            'fg_pct': 0.5,   # Field Goal Percentage
            'ts_pct': 0.5    # True Shooting Percentage
        }
        
        rating = 0
        for stat, weight in weights.items():
            if stat in self.stats:
                if stat in ['fg_pct', 'ts_pct']:
                    rating += (self.stats[stat] / 100) * weight * 100
                else:
                    rating += self.stats[stat] * weight
        
        # Add bonuses for exceptional performance
        if self.stats.get('pts', 0) >= 25: rating += 10
        if self.stats.get('ast', 0) >= 8: rating += 8
        if self.stats.get('reb', 0) >= 10: rating += 8
        if self.stats.get('stl', 0) >= 2: rating += 5
        if self.stats.get('blk', 0) >= 2: rating += 5
        
        return rating

class TeamSimulator:
    def __init__(self):
        # Cache for player ratings
        self._player_rating_cache = {}
        # Cache for team ratings
        self._team_rating_cache = {}
        # Cache for player stats
        self._player_stats_cache = {}
        
    def _get_player_stats(self, player_name: str) -> Optional[Dict]:
        """Get player stats with caching"""
        if player_name in self._player_stats_cache:
            return self._player_stats_cache[player_name]
            
        stats = get_player_stats(player_name)
        if stats:
            self._player_stats_cache[player_name] = stats
        return stats
        
    def calculate_player_rating(self, player_name: str) -> float:
        """Calculate a player's rating based on their stats"""
        try:
            # Check cache first
            if player_name in self._player_rating_cache:
                return self._player_rating_cache[player_name]
                
            player_data = self._get_player_stats(player_name)
            if not player_data:
                return 0.0
                
            stats = player_data['stats']
            rating = 0
            
            # Calculate base rating from weighted stats
            weights = {
                'pts': 1.0,      # Points (major factor)
                'ast': 1.0,      # Assists (playmaking)
                'reb': 0.8,      # Rebounds
                'stl': 0.7,      # Steals
                'blk': 0.7,      # Blocks
                'fg_pct': 0.5,   # Field Goal Percentage
                'ts_pct': 0.5    # True Shooting Percentage
            }
            
            for stat, weight in weights.items():
                if stat in stats:
                    if stat in ['fg_pct', 'ts_pct']:
                        rating += (float(stats[stat]) / 100) * weight * 100
                    else:
                        rating += float(stats[stat]) * weight
            
            # Add bonuses for exceptional performance
            if float(stats.get('pts', 0)) >= 25: rating += 10
            if float(stats.get('ast', 0)) >= 8: rating += 8
            if float(stats.get('reb', 0)) >= 10: rating += 8
            if float(stats.get('stl', 0)) >= 2: rating += 5
            if float(stats.get('blk', 0)) >= 2: rating += 5
            
            # Cache the result
            self._player_rating_cache[player_name] = round(rating, 1)
            return self._player_rating_cache[player_name]
            
        except Exception as e:
            logger.error(f"Error calculating rating for {player_name}: {str(e)}")
            return 0.0
            
    def calculate_team_rating(self, team: List[str]) -> float:
        """Calculate a team's rating based on its players"""
        try:
            # Create a cache key
            team_key = tuple(sorted(team))
            if team_key in self._team_rating_cache:
                return self._team_rating_cache[team_key]
                
            # Calculate team rating
            team_rating = sum(self.calculate_player_rating(player) for player in team)
            
            # Cache the result
            self._team_rating_cache[team_key] = round(team_rating, 1)
            return self._team_rating_cache[team_key]
            
        except Exception as e:
            logger.error(f"Error calculating team rating: {str(e)}")
            return 0.0
            
    def simulate_game(self, team1: List[str], team2: List[str]) -> Dict:
        """Simulate a game between two teams"""
        try:
            # Calculate team ratings
            team1_rating = self.calculate_team_rating(team1)
            team2_rating = self.calculate_team_rating(team2)
            
            # Add some randomness
            team1_rating += random.uniform(-5, 5)
            team2_rating += random.uniform(-5, 5)
            
            # Determine winner
            if team1_rating > team2_rating:
                winner = team1
                loser = team2
                score_diff = int((team1_rating - team2_rating) * 0.5)
            else:
                winner = team2
                loser = team1
                score_diff = int((team2_rating - team1_rating) * 0.5)
                
            # Generate realistic score
            base_score = random.randint(90, 120)
            winner_score = base_score + score_diff
            loser_score = base_score - score_diff
            
            return {
                'winner': winner,
                'loser': loser,
                'score': f"{winner_score}-{loser_score}",
                'team1_rating': round(team1_rating, 1),
                'team2_rating': round(team2_rating, 1)
            }
            
        except Exception as e:
            logger.error(f"Error simulating game: {str(e)}")
            return {}
            
    def simulate_season(self, teams: Dict[str, List[str]], games_per_team: int = 82) -> Dict:
        """Simulate a full season for all teams"""
        try:
            standings = {team: {'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0} for team in teams.keys()}
            
            # Simulate games
            for _ in range(games_per_team):
                for team1_name, team1 in teams.items():
                    # Randomly select opponent
                    team2_name = random.choice([t for t in teams.keys() if t != team1_name])
                    team2 = teams[team2_name]
                    
                    # Simulate game
                    result = self.simulate_game(team1, team2)
                    if not result:
                        continue
                        
                    # Update standings
                    if team1_name in result['winner']:
                        standings[team1_name]['wins'] += 1
                        standings[team2_name]['losses'] += 1
                    else:
                        standings[team1_name]['losses'] += 1
                        standings[team2_name]['wins'] += 1
                        
                    # Update points
                    winner_score, loser_score = map(int, result['score'].split('-'))
                    if team1_name in result['winner']:
                        standings[team1_name]['points_for'] += winner_score
                        standings[team1_name]['points_against'] += loser_score
                        standings[team2_name]['points_for'] += loser_score
                        standings[team2_name]['points_against'] += winner_score
                    else:
                        standings[team1_name]['points_for'] += loser_score
                        standings[team1_name]['points_against'] += winner_score
                        standings[team2_name]['points_for'] += winner_score
                        standings[team2_name]['points_against'] += loser_score
            
            # Calculate point differential
            for team in standings:
                standings[team]['point_diff'] = standings[team]['points_for'] - standings[team]['points_against']
            
            # Sort standings by wins, then point differential
            sorted_standings = dict(sorted(
                standings.items(),
                key=lambda x: (x[1]['wins'], x[1]['point_diff']),
                reverse=True
            ))
            
            return sorted_standings
            
        except Exception as e:
            logger.error(f"Error simulating season: {str(e)}")
            return {}
            
    def get_player_stats_summary(self, player_name: str) -> Dict:
        """Get a summary of a player's stats including 3-season average"""
        try:
            player_data = get_player_stats(player_name)
            if not player_data:
                return {}
                
            current_stats = player_data['stats']
            three_season_avg = player_data['3_season_avg']
            
            return {
                'name': player_name,
                'position': player_data['position'],
                'team': player_data['team'],
                'cost': player_data['cost'],
                'rating': player_data['rating'],
                'current_stats': current_stats,
                'three_season_avg': three_season_avg
            }
            
        except Exception as e:
            logger.error(f"Error getting stats summary for {player_name}: {str(e)}")
            return {}

    def clear_cache(self):
        """Clear all caches to free memory"""
        self._player_rating_cache.clear()
        self._team_rating_cache.clear()
        self._player_stats_cache.clear()

def main():
    # Test the simulator
    simulator = TeamSimulator()
    players = simulator.get_random_players()
    if players:
        print("Random players:", players)
    else:
        print("Failed to get random players")

# Add API endpoints
from flask import Flask, jsonify, request

app = Flask(__name__)
simulator = TeamSimulator()

@app.route('/player_pool', methods=['GET'])
def get_player_pool():
    try:
        players = simulator.get_random_players()
        if players:
            return jsonify(players)
        else:
            return jsonify({'error': 'Failed to get player pool'}), 500
    except Exception as e:
        logger.error(f"Error in get_player_pool: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        if not data or 'players' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        # Create team from request data
        team = TeamSimulator()
        for player_data in data['players']:
            try:
                player = Player(player_data['name'], player_data['stats'])
                team.add_player(player)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
        # Simulate season
        wins, losses = team.simulate_season()
        
        return jsonify({
            'wins': wins,
            'losses': losses,
            'win_probability': team.win_probability,
            'team_quality': team.team_quality,
            'team_stats': team.get_team_stats()
        })
        
    except Exception as e:
        logger.error(f"Error in simulate: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 