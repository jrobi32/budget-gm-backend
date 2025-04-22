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