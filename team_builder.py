import random
import json
from team_simulator import TeamSimulator
from season_simulator import SeasonSimulator, display_season_stats
import sys
import time
from typing import Dict, List, Optional
import logging
from .player_stats import get_player_stats, get_all_player_stats
from .static_player_pool import get_static_player_pool, get_players_by_cost

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_player_pool():
    """Load the player pool from the JSON file"""
    try:
        with open('player_pool.json', 'r') as f:
            data = json.load(f)
            return data['players']  # Return the list of players directly
    except Exception as e:
        print(f"Error loading player pool: {str(e)}")
        return []

def get_random_players(player_pool, cost_category, count=5):
    """Get random players from a specific cost category"""
    players_in_category = [p for p in player_pool if p['cost'] == cost_category]
    if not players_in_category:
        print(f"No players found in {cost_category} category")
        return []
    return random.sample(players_in_category, min(count, len(players_in_category)))

def display_player_options(player_pool):
    """Display random players from each cost category"""
    print("\nAvailable Players:")
    print("----------------")
    
    for cost in ['$5', '$4', '$3', '$2', '$1']:
        print(f"\n{cost} Players:")
        players = get_random_players(player_pool, cost)
        for i, player in enumerate(players, 1):
            stats = player['stats']
            print(f"{i}. {player['name']} - PTS: {stats['pts']:.1f}, AST: {stats['ast']:.1f}, REB: {stats['reb']:.1f}, "
                  f"STL: {stats['stl']:.1f}, BLK: {stats['blk']:.1f}, FG%: {stats['fg_pct']:.1f}, TS%: {stats['ts_pct']:.1f}")

class TeamBuilder:
    def __init__(self, budget: int = 15):
        self.budget = budget
        self.players = []
        self.positions = {
            'PG': 0,
            'SG': 0,
            'SF': 0,
            'PF': 0,
            'C': 0
        }
        # Cache for player data
        self._player_data_cache = {}
        
    def _get_player_data(self, player_name: str) -> Optional[Dict]:
        """Get player data with caching"""
        if player_name in self._player_data_cache:
            return self._player_data_cache[player_name]
            
        player_data = get_player_stats(player_name)
        if player_data:
            self._player_data_cache[player_name] = player_data
        return player_data
        
    def add_player(self, player_name: str) -> bool:
        """Add a player to the team"""
        try:
            if len(self.players) >= 5:
                logger.warning("Team already has 5 players")
                return False
                
            player_data = self._get_player_data(player_name)
            if not player_data:
                logger.warning(f"Player {player_name} not found")
                return False
                
            # Check if player is already in team
            if player_name in self.players:
                logger.warning(f"Player {player_name} is already in the team")
                return False
                
            # Calculate total cost with new player
            total_cost = sum(self._get_player_data(p)['cost'] for p in self.players) + player_data['cost']
            if total_cost > self.budget:
                logger.warning(f"Adding {player_name} would exceed the ${self.budget} budget")
                return False
                
            # Check position balance
            position = player_data['position']
            if self.positions[position] >= 2:  # Max 2 players per position
                logger.warning(f"Already have 2 {position}s in the team")
                return False
                
            # Add player
            self.players.append(player_name)
            self.positions[position] += 1
            
            logger.info(f"Added {player_name} to the team")
            return True
            
        except Exception as e:
            logger.error(f"Error adding player {player_name}: {str(e)}")
            return False
            
    def remove_player(self, player_name: str) -> bool:
        """Remove a player from the team"""
        try:
            if player_name not in self.players:
                logger.warning(f"Player {player_name} not in team")
                return False
                
            player_data = self._get_player_data(player_name)
            if not player_data:
                logger.warning(f"Player {player_name} not found")
                return False
                
            # Remove player
            self.players.remove(player_name)
            self.positions[player_data['position']] -= 1
            
            logger.info(f"Removed {player_name} from the team")
            return True
            
        except Exception as e:
            logger.error(f"Error removing player {player_name}: {str(e)}")
            return False
            
    def get_team_stats(self) -> Dict:
        """Get team statistics"""
        try:
            if not self.players:
                return {}
                
            stats = {}
            for stat in ['pts', 'ast', 'reb', 'stl', 'blk', 'fg_pct', 'ts_pct', '3pt_pct', 'ft_pct']:
                values = [self._get_player_data(p)['stats'][stat] for p in self.players if stat in self._get_player_data(p)['stats']]
                if values:
                    stats[stat] = sum(values) / len(values)
                    
            return stats
            
        except Exception as e:
            logger.error(f"Error getting team stats: {str(e)}")
            return {}
            
    def get_team_cost(self) -> int:
        """Get total cost of the team"""
        try:
            return sum(self._get_player_data(p)['cost'] for p in self.players)
        except Exception as e:
            logger.error(f"Error calculating team cost: {str(e)}")
            return 0
            
    def get_remaining_budget(self) -> int:
        """Get remaining budget"""
        return self.budget - self.get_team_cost()
        
    def is_team_complete(self) -> bool:
        """Check if team has 5 players"""
        return len(self.players) == 5
        
    def is_team_valid(self) -> bool:
        """Check if team is valid (5 players, within budget, and balanced positions)"""
        if not self.is_team_complete():
            return False
            
        if self.get_team_cost() > self.budget:
            return False
            
        # Check position balance
        for position, count in self.positions.items():
            if count > 2:  # Max 2 players per position
                return False
                
        return True
        
    def get_team_summary(self) -> Dict:
        """Get a summary of the team"""
        try:
            return {
                'players': self.players,
                'positions': self.positions,
                'stats': self.get_team_stats(),
                'cost': self.get_team_cost(),
                'remaining_budget': self.get_remaining_budget(),
                'is_valid': self.is_team_valid()
            }
        except Exception as e:
            logger.error(f"Error getting team summary: {str(e)}")
            return {}
            
    def get_player_details(self, player_name: str) -> Dict:
        """Get detailed information about a player in the team"""
        try:
            if player_name not in self.players:
                return {}
                
            player_data = self._get_player_data(player_name)
            if not player_data:
                return {}
                
            return {
                'name': player_name,
                'position': player_data['position'],
                'team': player_data['team'],
                'cost': player_data['cost'],
                'rating': player_data['rating'],
                'stats': player_data['stats'],
                'three_season_avg': player_data['3_season_avg']
            }
        except Exception as e:
            logger.error(f"Error getting player details for {player_name}: {str(e)}")
            return {}
            
    def get_available_players(self, cost: str) -> List[Dict]:
        """Get available players for a specific cost"""
        try:
            return get_players_by_cost(cost)
        except Exception as e:
            logger.error(f"Error getting available players for cost {cost}: {str(e)}")
            return []

def build_team():
    """Main function to build a team"""
    print("NBA Team Builder")
    print("===============")
    print("This program will help you build a team of 5 players with a $15 budget.")
    print("You'll be shown 5 random players from each cost category ($5, $4, $3, $2, $1).")
    
    player_pool = load_player_pool()
    if not player_pool:
        return
    
    team = []
    budget = 15
    
    while len(team) < 5:
        print(f"\nCurrent Team ({len(team)}/5 players):")
        total_cost = sum(int(p['cost'][1:]) for p in team)
        print(f"Total Cost: ${total_cost}")
        print(f"Remaining Budget: ${budget - total_cost}")
        
        if team:
            print("\nCurrent Players:")
            for i, player in enumerate(team, 1):
                print(f"{i}. {player['name']} ({player['cost']})")
        
        display_player_options(player_pool)
        
        print("\nOptions:")
        print("1. Select a player")
        print("2. Remove a player")
        print("3. Refresh player options")
        print("4. View current team stats")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            cost = input("Enter the cost category ($5, $4, $3, $2, $1): ")
            if cost not in ['$5', '$4', '$3', '$2', '$1']:
                print("Invalid cost category")
                continue
                
            players = get_random_players(player_pool, cost)
            if not players:
                continue
                
            print(f"\nAvailable {cost} Players:")
            for i, player in enumerate(players, 1):
                print(f"{i}. {player['name']}")
                
            try:
                player_choice = int(input("Select a player (1-5): ")) - 1
                if 0 <= player_choice < len(players):
                    selected_player = players[player_choice]
                    if total_cost + int(cost[1:]) <= budget:
                        team.append(selected_player)
                        print(f"Added {selected_player['name']} to your team")
                    else:
                        print("Not enough budget remaining")
                else:
                    print("Invalid player selection")
            except ValueError:
                print("Invalid input")
                
        elif choice == '2':
            if not team:
                print("No players to remove")
                continue
                
            print("\nCurrent Team:")
            for i, player in enumerate(team, 1):
                print(f"{i}. {player['name']} ({player['cost']})")
                
            try:
                remove_choice = int(input("Select a player to remove (1-5): ")) - 1
                if 0 <= remove_choice < len(team):
                    removed_player = team.pop(remove_choice)
                    print(f"Removed {removed_player['name']} from your team")
                else:
                    print("Invalid player selection")
            except ValueError:
                print("Invalid input")
                
        elif choice == '3':
            print("Refreshing player options...")
            
        elif choice == '4':
            if not team:
                print("No players in team")
                continue
                
            print("\nTeam Statistics:")
            total_pts = sum(p['stats']['pts'] for p in team)
            total_ast = sum(p['stats']['ast'] for p in team)
            total_reb = sum(p['stats']['reb'] for p in team)
            total_stl = sum(p['stats']['stl'] for p in team)
            total_blk = sum(p['stats']['blk'] for p in team)
            
            print(f"Total Points: {total_pts:.1f}")
            print(f"Total Assists: {total_ast:.1f}")
            print(f"Total Rebounds: {total_reb:.1f}")
            print(f"Total Steals: {total_stl:.1f}")
            print(f"Total Blocks: {total_blk:.1f}")
            
        elif choice == '5':
            print("Exiting team builder")
            return
            
        else:
            print("Invalid choice")
    
    print("\nFinal Team:")
    total_cost = sum(int(p['cost'][1:]) for p in team)
    print(f"Total Cost: ${total_cost}")
    for i, player in enumerate(team, 1):
        print(f"{i}. {player['name']} ({player['cost']})")

if __name__ == "__main__":
    build_team() 