from data_fetcher import NBADataFetcher
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    fetcher = NBADataFetcher()
    
    # Get player pool using the fetcher's consolidated logic
    player_pool = fetcher.get_player_pool()
    
    if not player_pool:
        logger.error("No player pool available, using fallback player pool")
        # Load fallback player pool
        try:
            with open('fallback_player_pool.json', 'r') as f:
                fallback_data = json.load(f)
                logger.info("Successfully loaded fallback player pool")
                return
        except Exception as e:
            logger.error(f"Error loading fallback player pool: {str(e)}")
            return
    
    # Save to JSON file
    output = {
        'last_updated': datetime.now().isoformat(),
        'players': player_pool
    }
    
    with open('player_pool.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"Successfully saved {len(player_pool)} players to player_pool.json")
    
    # Also save as fallback
    with open('fallback_player_pool.json', 'w') as f:
        json.dump(output, f, indent=2)
    logger.info("Saved fallback player pool")

if __name__ == '__main__':
    main() 