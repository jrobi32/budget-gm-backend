import json

def combine_player_pools():
    # List of files to combine
    files = [
        'raw_player_pool.json',
        'raw_player_pool_part2.json',
        'raw_player_pool_part3.json'
    ]
    
    combined_players = []
    
    # Read and combine all files
    for file in files:
        try:
            with open(file, 'r') as f:
                players = json.load(f)
                combined_players.extend(players)
                print(f"Added {len(players)} players from {file}")
        except FileNotFoundError:
            print(f"Warning: {file} not found")
        except json.JSONDecodeError:
            print(f"Error: {file} is not valid JSON")
    
    # Save combined data
    with open('complete_player_pool.json', 'w') as f:
        json.dump(combined_players, f, indent=4)
    
    print(f"\nTotal players in complete pool: {len(combined_players)}")
    print("Saved to complete_player_pool.json")

if __name__ == "__main__":
    combine_player_pools() 