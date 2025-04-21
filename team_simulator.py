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
        self.cost = self._calculate_cost()
        
    def _calculate_cost(self) -> int:
        """Calculate player cost based on their stats"""
        # Basic stats weights
        weights = {
            'PTS': 0.40,      # Points (major factor)
            'AST': 0.25,      # Assists (playmaking)
            'REB': 0.20,      # Rebounds
            'STL': 0.05,      # Steals
            'BLK': 0.05,      # Blocks
            'FG_PCT': 0.05,   # Field Goal Percentage
            'TS_PCT': 0.05    # True Shooting Percentage
        }
        
        # Calculate weighted score
        score = 0
        for stat, weight in weights.items():
            if stat in self.stats:
                if stat in ['FG_PCT', 'TS_PCT']:
                    # Convert percentages to 0-1 scale
                    score += (self.stats[stat] / 100) * weight * 10
                else:
                    # Scale counting stats appropriately
                    score += self.stats[stat] * weight
        
        # Add bonuses for exceptional performance
        if self.stats['PTS'] >= 30:  # MVP-level scoring
            score += 20
        elif self.stats['PTS'] >= 25:  # All-Star level scoring
            score += 15
        elif self.stats['PTS'] >= 20:  # High-end starter scoring
            score += 10
        elif self.stats['PTS'] >= 15:  # Solid starter scoring
            score += 5
            
        if self.stats['AST'] >= 10:   # Elite playmaking
            score += 15
        elif self.stats['AST'] >= 7:  # All-Star playmaking
            score += 10
        elif self.stats['AST'] >= 5:  # Good playmaking
            score += 5
            
        if self.stats['REB'] >= 12:  # Elite rebounding
            score += 15
        elif self.stats['REB'] >= 10:  # All-Star rebounding
            score += 10
        elif self.stats['REB'] >= 7:  # Good rebounding
            score += 5
            
        if self.stats['STL'] + self.stats['BLK'] >= 3.0:  # Elite defense
            score += 10
        elif self.stats['STL'] + self.stats['BLK'] >= 2.0:  # Very good defense
            score += 5
            
        if self.stats['TS_PCT'] >= 0.65:  # Elite efficiency
            score += 10
        elif self.stats['TS_PCT'] >= 0.60:  # Very good efficiency
            score += 5
            
        # Apply games played adjustment
        games_played = self.stats.get('GP', 0)
        games_played_percentage = min(games_played / 246, 1.0)  # Cap at 100%
        
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
            
        # Calculate team quality based on player stats
        quality_metrics = {
            'PTS': 0.30,  # Scoring
            'AST': 0.20,  # Playmaking
            'REB': 0.15,  # Rebounding
            'STL': 0.10,  # Defense
            'BLK': 0.10,  # Defense
            'FG_PCT': 0.10,  # Efficiency
            'TS_PCT': 0.05   # Efficiency
        }
        
        # Calculate average stats for the team
        team_stats = {}
        for stat in quality_metrics.keys():
            values = [p.stats.get(stat, 0) for p in self.players]
            team_stats[stat] = sum(values) / len(values)
            
        # Calculate team quality score
        quality_score = 0
        for stat, weight in quality_metrics.items():
            if stat in team_stats:
                if stat in ['FG_PCT', 'TS_PCT']:
                    quality_score += (team_stats[stat] / 100) * weight * 10
                else:
                    quality_score += team_stats[stat] * weight
                    
        # Normalize quality score to 0-1 range
        self.team_quality = min(max(quality_score / 100, 0), 1)
        
        # Calculate win probability based on team quality
        # Using a sigmoid function to map quality to win probability
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
        for stat in ['PTS', 'AST', 'REB', 'STL', 'BLK', 'FG_PCT', 'TS_PCT']:
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
            return jsonify({'error': 'Missing players in request'}), 400

        players = data['players']
        result = simulator.simulate_team(players)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to simulate team'}), 500
    except Exception as e:
        logger.error(f"Error in simulate: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 