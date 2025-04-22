from data_fetcher import NBADataFetcher
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json
import random
import os
from datetime import datetime, timedelta

class PlayerPool:
    def __init__(self):
        self.data_fetcher = NBADataFetcher()
        self.players = {}  # Dictionary to store player costs
        self.player_stats = {}  # Dictionary to store player stats
        self._load_player_pool()
        
    def _load_player_pool(self):
        """
        Load the player pool from JSON file.
        If the file doesn't exist or is older than 24 hours, rebuild it.
        """
        try:
            # Check if file exists and is from today
            if os.path.exists('player_pool.json'):
                file_timestamp = datetime.fromtimestamp(os.path.getmtime('player_pool.json'))
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                if file_timestamp >= today:
                    print("Using today's cached player pool...")
                    with open('player_pool.json', 'r') as f:
                        data = json.load(f)
                        player_pool = data['players']
                        
                    # Convert JSON data to internal format
                    for player_data in player_pool:
                        player_name = player_data['name']
                        cost = int(player_data['cost'].replace('$', ''))
                        self.players[player_name] = {'cost': cost}
                        self.player_stats[player_name] = pd.Series(player_data['stats'])
                            
                    print(f"Loaded {len(self.players)} players from today's pool")
                    return
                
            print("Player pool not found or outdated. Building new pool...")
            self._build_player_pool()
            
        except Exception as e:
            print(f"Error loading player pool: {str(e)}")
            print("Building new pool...")
            self._build_player_pool()
            
    def _build_player_pool(self):
        """
        Build the complete NBA player pool and save it to a JSON file with timestamp
        """
        print("Building complete NBA player pool...")
        
        # Get player pool using the fetcher's consolidated logic
        player_pool = self.data_fetcher.get_player_pool()
        print(f"Found {len(player_pool)} active players")
        
        # Initialize categorized players
        categorized_players = {
            '5': [],  # Superstars
            '4': [],  # All-Stars
            '3': [],  # Quality starters
            '2': [],  # Solid role players
            '1': []   # Role players
        }
        
        # Process each player
        for player_data in player_pool:
            try:
                # Remove $ prefix from cost for internal storage
                cost = int(player_data['cost'].replace('$', ''))
                categorized_players[str(cost)].append(player_data)
                
                # Store in internal format
                player_name = player_data['name']
                self.players[player_name] = {'cost': cost}
                self.player_stats[player_name] = pd.Series(player_data['stats'])
                
            except Exception as e:
                print(f"Error processing player: {str(e)}")
                continue
        
        # Save to JSON file with timestamp
        data = {
            'timestamp': datetime.now().isoformat(),
            'players': player_pool
        }
        
        with open('player_pool.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("\nPlayer pool saved to player_pool.json")
        print("Category counts:")
        for cost, players in categorized_players.items():
            print(f"${cost}: {len(players)} players")
            
    def get_random_players(self, cost, count=5):
        """
        Get random players from a specific cost category
        """
        players_in_category = [p for p, data in self.players.items() if data['cost'] == cost]
        if len(players_in_category) < count:
            print(f"Warning: Only {len(players_in_category)} players available in ${cost} category")
            return players_in_category
        return random.sample(players_in_category, count)
        
    def get_player_cost(self, player_name):
        """
        Get the cost of a specific player
        """
        return self.players.get(player_name, {}).get('cost', 0)
        
    def get_player_stats(self, player_name):
        """
        Get the stats of a specific player
        """
        return self.player_stats.get(player_name)
        
    def _calculate_player_cost(self, stats):
        """
        Calculate player cost based on performance metrics
        Returns cost from 1-5 dollars
        """
        if stats is None:
            return 1
            
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
            if stat in stats:
                if stat in ['FG_PCT', 'TS_PCT']:
                    # Convert percentages to 0-1 scale
                    score += (stats[stat] / 100) * weight * 10
                else:
                    # Scale counting stats appropriately
                    score += stats[stat] * weight
        
        # Add bonuses for exceptional performance
        if stats['PTS'] >= 30:  # MVP-level scoring
            score += 20
        elif stats['PTS'] >= 25:  # All-Star level scoring
            score += 15
        elif stats['PTS'] >= 20:  # High-end starter scoring
            score += 10
        elif stats['PTS'] >= 15:  # Solid starter scoring
            score += 5
            
        if stats['AST'] >= 10:   # Elite playmaking
            score += 15
        elif stats['AST'] >= 7:  # All-Star playmaking
            score += 10
        elif stats['AST'] >= 5:  # Good playmaking
            score += 5
            
        if stats['REB'] >= 12:  # Elite rebounding
            score += 15
        elif stats['REB'] >= 10:  # All-Star rebounding
            score += 10
        elif stats['REB'] >= 7:  # Good rebounding
            score += 5
            
        if stats['STL'] + stats['BLK'] >= 3.0:  # Elite defense
            score += 10
        elif stats['STL'] + stats['BLK'] >= 2.0:  # Very good defense
            score += 5
            
        if stats['TS_PCT'] >= 0.65:  # Elite efficiency
            score += 10
        elif stats['TS_PCT'] >= 0.60:  # Very good efficiency
            score += 5
            
        # Apply games played adjustment
        games_played = stats.get('GP', 0)
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
        
    def get_available_players(self) -> List[Tuple[str, float]]:
        """
        Get list of available players with their costs
        """
        return [(player, self.get_player_cost(player)) for player in self.players.keys()]
        
    def validate_team(self, selected_players: List[str], budget: float = 15.0) -> bool:
        """
        Validate if a team is within budget and has exactly 5 players
        """
        if len(selected_players) != 5:
            return False
            
        total_cost = sum(self.get_player_cost(player) for player in selected_players)
        return total_cost <= budget

def main():
    # Test the player pool with specific players
    pool = PlayerPool()
    
    # Test with a larger sample of players across all tiers
    test_players = [
        # MVP Candidates
        "Nikola Jokic",
        "Shai Gilgeous-Alexander",
        "Luka Doncic",
        "Joel Embiid",
        "Giannis Antetokounmpo",
        
        # All-Stars
        "Jayson Tatum",
        "Devin Booker",
        "Anthony Davis",
        "Donovan Mitchell",
        "De'Aaron Fox",
        
        # Quality Starters
        "Mikal Bridges",
        "CJ McCollum",
        "Draymond Green",
        "Kristaps Porzingis",
        "Fred VanVleet",
        
        # Solid Role Players
        "Kyle Kuzma",
        "Bojan Bogdanovic",
        "Gary Trent Jr.",
        "Josh Hart",
        "Marcus Smart",
        
        # Role Players
        "Pat Connaughton",
        "Georges Niang",
        "Jae Crowder",
        "Alex Caruso",
        "Joe Harris"
    ]
    
    print("Building player pool with test players...")
    for player in test_players:
        stats = pool.data_fetcher.get_player_stats(player)
        if stats is not None:
            value = pool._calculate_player_value(stats)
            cost = pool._value_to_cost(value)
            pool.players[player] = {'cost': cost}
            pool.player_stats[player] = stats
    
    # Print players by tier with more detailed stats
    print("\nPlayers by Cost Tier:")
    print("-" * 80)
    
    players_by_tier = {}
    for player, cost in pool.get_available_players():
        if cost not in players_by_tier:
            players_by_tier[cost] = []
        players_by_tier[cost].append((player, pool.get_player_stats(player)))
    
    for cost in sorted(players_by_tier.keys(), reverse=True):
        print(f"\n${cost} Players:")
        print("-" * 40)
        for player, stats in players_by_tier[cost]:
            print(f"\n{player}")
            print(f"PPG: {stats['PTS']:.1f}, APG: {stats['AST']:.1f}, RPG: {stats['REB']:.1f}")
            print(f"Stocks: {stats['STOCKS']:.1f}, TS%: {stats['TS_PCT']:.1%}")
            print(f"USG%: {stats['USG_PCT']:.1%}, Minutes: {stats['MIN']:.1f}")
    
    # Show example team combinations
    print("\n" + "-" * 80)
    print("\nExample Team Combinations ($15 budget):")
    print("-" * 80)
    
    # Example 1: Superstar-centric team
    team1 = ["Nikola Jokic", "Kyle Kuzma", "Josh Hart", "Georges Niang", "Alex Caruso"]
    total_cost1 = sum(pool.get_player_cost(player) for player in team1)
    print(f"\nTeam 1 - Superstar Build (Total: ${total_cost1}):")
    for player in team1:
        cost = pool.get_player_cost(player)
        print(f"- {player}: ${cost}")
    
    # Example 2: Balanced team
    team2 = ["De'Aaron Fox", "Fred VanVleet", "Bojan Bogdanovic", "Marcus Smart", "Joe Harris"]
    total_cost2 = sum(pool.get_player_cost(player) for player in team2)
    print(f"\nTeam 2 - Balanced Build (Total: ${total_cost2}):")
    for player in team2:
        cost = pool.get_player_cost(player)
        print(f"- {player}: ${cost}")

if __name__ == "__main__":
    main() 