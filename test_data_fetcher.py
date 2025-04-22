from data_fetcher import NBADataFetcher
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_fetcher():
    fetcher = NBADataFetcher()
    
    # Test 1: Get player stats
    logger.info("Testing get_player_stats()...")
    df = fetcher.get_player_stats()
    logger.info(f"Retrieved stats for {len(df)} players")
    logger.info(f"Sample player stats:\n{df[['PLAYER_NAME', 'PTS', 'AST', 'REB', 'STL', 'BLK', 'FG_PCT', 'TS_PCT']].head()}")
    
    # Test 2: Get active players
    logger.info("\nTesting get_active_players()...")
    players = fetcher.get_active_players()
    logger.info(f"Retrieved {len(players)} active players")
    
    # Print sample players from each cost tier
    cost_tiers = {'$5': [], '$4': [], '$3': [], '$2': [], '$1': []}
    for player in players:
        cost_tiers[player['cost']].append(player)
    
    logger.info("\nSample players by cost tier:")
    for cost, tier_players in cost_tiers.items():
        if tier_players:
            sample = tier_players[0]
            logger.info(f"\n{cost} player example:")
            logger.info(f"Name: {sample['name']}")
            logger.info(f"Stats: {sample['stats']}")
    
    # Test 3: Get top scorers
    logger.info("\nTesting get_top_scorers()...")
    top_scorers = fetcher.get_top_scorers(limit=5)
    logger.info("Top 5 scorers:")
    for player in top_scorers:
        logger.info(f"{player['PLAYER_NAME']}: {player['PTS']} PPG")
    
    # Test 4: Get bottom scorers
    logger.info("\nTesting get_bottom_scorers()...")
    bottom_scorers = fetcher.get_bottom_scorers(limit=5)
    logger.info("Bottom 5 scorers:")
    for player in bottom_scorers:
        logger.info(f"{player['PLAYER_NAME']}: {player['PTS']} PPG")

if __name__ == '__main__':
    test_data_fetcher() 