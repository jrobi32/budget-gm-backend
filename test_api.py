from nba_api.stats.endpoints import commonallplayers
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_api_connection():
    try:
        # Test direct requests to NBA API
        response = requests.get('https://stats.nba.com/stats/commonallplayers', 
                              params={'LeagueID': '00', 'Season': '2023-24', 'IsOnlyCurrentSeason': 1},
                              headers={
                                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                  'Accept': 'application/json, text/plain, */*',
                                  'Accept-Language': 'en-US,en;q=0.9',
                                  'Accept-Encoding': 'gzip, deflate, br',
                                  'x-nba-stats-origin': 'stats',
                                  'x-nba-stats-token': 'true',
                                  'Connection': 'keep-alive',
                                  'Host': 'stats.nba.com',
                                  'Referer': 'https://www.nba.com/'
                              },
                              timeout=30)
        
        logger.info(f"Direct API Response Status: {response.status_code}")
        logger.info(f"Direct API Response Headers: {response.headers}")
        
        # Test nba_api package
        players = commonallplayers.CommonAllPlayers(
            is_only_current_season=1,
            timeout=30
        )
        
        logger.info("NBA API package test successful")
        logger.info(f"Number of players found: {len(players.get_data_frames()[0])}")
        
    except Exception as e:
        logger.error(f"API Test Error: {str(e)}")

if __name__ == '__main__':
    test_api_connection() 