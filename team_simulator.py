import json
import pandas as pd
import numpy as np
import random
import math
import logging
from typing import Dict, List, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    def __init__(self, budget: int = 15):
        self.budget = budget
        self.players = []
        self.team_quality = 0
        self.win_probability = 0.5
        
    def add_player(self, player: Player):
        """Add a player to the team"""
        if len(self.players) >= 5:
            raise ValueError("Team already has 5 players")
            
        total_cost = sum(p.cost for p in self.players) + player.cost
        if total_cost > self.budget:
            raise ValueError(f"Adding this player would exceed the ${self.budget} budget")
            
        self.players.append(player)
        self._update_team_quality()
        
    def _update_team_quality(self):
        """Update team quality based on current players"""
        if not self.players:
            self.team_quality = 0
            self.win_probability = 0.5
            return
            
        # Calculate team quality based on player ratings
        total_rating = sum(p.get_rating() for p in self.players)
        avg_rating = total_rating / len(self.players)
        
        # Calculate team balance (how well players complement each other)
        balance_score = 0
        if len(self.players) > 1:
            # Check for complementary skills
            has_scorer = any(p.stats.get('pts', 0) >= 20 for p in self.players)
            has_playmaker = any(p.stats.get('ast', 0) >= 6 for p in self.players)
            has_defender = any(p.stats.get('stl', 0) + p.stats.get('blk', 0) >= 2 for p in self.players)
            has_rebounder = any(p.stats.get('reb', 0) >= 8 for p in self.players)
            
            balance_score = sum([has_scorer, has_playmaker, has_defender, has_rebounder]) / 4
        
        # Combine ratings and balance
        self.team_quality = (avg_rating * 0.7 + balance_score * 0.3) / 100
        
        # Calculate win probability using sigmoid function
        self.win_probability = 1 / (1 + np.exp(-10 * (self.team_quality - 0.5)))
        
    def simulate_game(self) -> bool:
        """Simulate a single game and return whether the team won"""
        if not self.players:
            raise ValueError("Cannot simulate game with empty team")
            
        # Add some randomness to the win probability
        adjusted_prob = self.win_probability + random.uniform(-0.1, 0.1)
        adjusted_prob = max(min(adjusted_prob, 0.95), 0.05)  # Keep between 5% and 95%
        
        return random.random() < adjusted_prob
        
    def simulate_season(self, num_games: int = 82) -> Tuple[int, int]:
        """Simulate a full season and return wins and losses"""
        if not self.players:
            raise ValueError("Cannot simulate season with empty team")
            
        wins = 0
        losses = 0
        
        for _ in range(num_games):
            if self.simulate_game():
                wins += 1
            else:
                losses += 1
                
        return wins, losses
        
    def get_team_stats(self) -> Dict:
        """Get team statistics"""
        if not self.players:
            return {}
            
        stats = {}
        for stat in ['pts', 'ast', 'reb', 'stl', 'blk', 'fg_pct', 'ts_pct']:
            values = [p.stats.get(stat, 0) for p in self.players]
            stats[stat] = sum(values) / len(values)
            
        return stats
        
    def get_team_cost(self) -> int:
        """Get total cost of the team"""
        return sum(p.cost for p in self.players)
        
    def get_remaining_budget(self) -> int:
        """Get remaining budget"""
        return self.budget - self.get_team_cost()
        
    def is_team_complete(self) -> bool:
        """Check if team has 5 players"""
        return len(self.players) == 5
        
    def is_team_valid(self) -> bool:
        """Check if team is valid (5 players and within budget)"""
        return self.is_team_complete() and self.get_team_cost() <= self.budget

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