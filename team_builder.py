import random
import json
from team_simulator import TeamSimulator
from season_simulator import SeasonSimulator, display_season_stats
import sys
import time

def load_player_pool():
    """Load the player pool from the JSON file"""
    try:
        with open('player_pool.json', 'r') as f:
            player_pool = json.load(f)
            print(f"Loaded player pool with {sum(len(players) for players in player_pool['players'].values())} players")
            print(f"Number of players in each category:")
            for cost, players in player_pool['players'].items():
                print(f"${cost}: {len(players)} players")
                if players:
                    print(f"First player in ${cost}: {players[0]['name']}")
            return player_pool['players']
    except FileNotFoundError:
        print("Error: player_pool.json not found. Please run player_pool.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading player pool: {e}")
        sys.exit(1)

def get_random_players(player_pool, category, count=5):
    """Get random players from a specific cost category"""
    if category not in player_pool:
        print(f"Warning: Category ${category} not found in player pool")
        return []
    players = player_pool[category]
    if len(players) < count:
        print(f"Warning: Not enough players in ${category} category (have {len(players)}, need {count})")
        return players
    
    selected_players = random.sample(players, count)
    print(f"Selected {len(selected_players)} players from ${category} category:")
    for player in selected_players:
        print(f"  - {player['name']}")
    return selected_players

def display_player_options(player_pool, show_stats=False):
    """Display 5 random players from each cost category"""
    print("\nPlayer Options:")
    print("==============")
    
    for cost in ["5", "4", "3", "2", "1"]:
        print(f"\n${cost} Players:")
        players = get_random_players(player_pool, cost)
        for player in players:
            if show_stats:
                stats = player['stats']
                print(f"{player['name']}")
                print(f"   Points: {stats['PTS']:.1f} | Rebounds: {stats['REB']:.1f} | Assists: {stats['AST']:.1f}")
                print(f"   Steals: {stats['STL']:.1f} | Blocks: {stats['BLK']:.1f}")
                print(f"   FG%: {stats['FG_PCT']:.3f} | TS%: {stats['TS_PCT']:.3f}")
                print(f"   Minutes: {stats['MIN']:.1f} | Games: {stats['GP']:.1f}")
                print()
            else:
                print(f"{player['name']}")

def build_team():
    """Build a team by selecting players from the available options"""
    # Load player pool
    player_pool = load_player_pool()
    
    # Initialize team simulator
    simulator = TeamSimulator(budget=15)  # $15 budget
    selected_players = []
    remaining_budget = 15  # $15 budget
    
    print("\nSelect your team (5 players total, budget of $15):")
    print("===============================================")
    
    # Get initial set of random players for each category
    displayed_players = {}
    for cost in ["5", "4", "3", "2", "1"]:
        displayed_players[cost] = get_random_players(player_pool, cost)
    
    while len(selected_players) < 5:
        # Display current team status
        print("\n" + "="*50)
        print("CURRENT TEAM STATUS")
        print("="*50)
        print(f"Players selected: {len(selected_players)}/5")
        print(f"Remaining budget: ${remaining_budget}")
        if selected_players:
            print("\nCurrent team:")
            total_cost = 0
            for player, cost in selected_players:
                total_cost += int(cost)
                print(f"- {player['name']} (${cost})")
            print(f"Total spent: ${total_cost}")
        print("="*50)
        
        # Display available players
        print("\nAvailable Players:")
        print("================")
        
        # Create a name-to-player mapping
        name_to_player = {}
        
        for cost in ["5", "4", "3", "2", "1"]:
            # Only show players we can afford
            if int(cost) <= remaining_budget:
                print(f"\n${cost} Players:")
                players = displayed_players[cost]
                for player in players:
                    name = player['name']
                    # Add both full name and individual parts to the mapping
                    name_parts = name.split()
                    for part in name_parts:
                        name_to_player[part.lower()] = (player, int(cost))
                    name_to_player[name.lower()] = (player, int(cost))
                    
                    print(f"{name}")
        
        print("\nSelect a player by entering their name (or 'r' to refresh options, 'q' to quit):")
        
        try:
            choice = input("> ").strip().lower()
            if choice == 'q':
                break
            elif choice == 'r':
                # Refresh the displayed players
                for cost in ["5", "4", "3", "2", "1"]:
                    displayed_players[cost] = get_random_players(player_pool, cost)
                continue
                
            if choice in name_to_player:
                selected_player, cost = name_to_player[choice]
                
                if cost <= remaining_budget:
                    selected_players.append((selected_player, cost))
                    remaining_budget -= cost
                    print(f"\nAdded {selected_player['name']} (${cost}) to your team!")
                    # Remove the selected player from displayed options
                    displayed_players[str(cost)].remove(selected_player)
                else:
                    print(f"Not enough budget for {selected_player['name']} (costs ${cost})")
            else:
                print("Player not found. Please try again.")
                
        except KeyboardInterrupt:
            print("\nTeam building cancelled.")
            return None
    
    if len(selected_players) == 5:
        print("\n" + "="*50)
        print("TEAM COMPLETE!")
        print("="*50)
        print("\nYour final team:")
        total_cost = 0
        for player, cost in selected_players:
            total_cost += cost
            print(f"- {player['name']} (${cost})")
        print(f"\nTotal spent: ${total_cost}")
        print("="*50)
        return [player for player, _ in selected_players]
    else:
        print("\nTeam incomplete. You need 5 players.")
        return None

if __name__ == "__main__":
    print("NBA Team Builder")
    print("===============")
    print("This program will help you build a team of 5 players with a $15 budget.")
    print("You'll be shown 5 random players from each cost category ($5, $4, $3, $2, $1).")
    print("Select players to add to your team.")
    
    team = build_team()
    if team:
        print("\nWould you like to simulate this team's performance? (y/n)")
        if input("> ").lower() == 'y':
            # Create season simulator
            season_sim = SeasonSimulator(team)
            season_sim.simulate_season()
            
            # Display final record
            print(f"\nFinal Record: {season_sim.wins}-{season_sim.losses}")
            
            # Display season stats
            stats = season_sim.get_season_stats()
            display_season_stats(stats) 