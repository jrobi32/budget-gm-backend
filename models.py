import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyChallenge:
    def __init__(self, date: str):
        self.date = date
        self.players = []
        self.submissions = []
        self._load_challenge()
        
    def _load_challenge(self):
        """Load challenge data from file"""
        try:
            file_path = f"data/challenges/{self.date}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.players = data.get('players', [])
                    self.submissions = data.get('submissions', [])
            else:
                self._generate_new_challenge()
        except Exception as e:
            logger.error(f"Error loading challenge: {str(e)}")
            self._generate_new_challenge()
            
    def _generate_new_challenge(self):
        """Generate a new daily challenge"""
        try:
            logger.info("Starting to generate new challenge...")
            # Load player pool
            with open('player_pool.json', 'r') as f:
                player_pool = json.load(f)
                logger.info(f"Loaded player pool with {len(player_pool['players'])} players")
                
            # Select players from each category
            categories = ['5', '4', '3', '2', '1']
            selected_players = []
            
            # Group players by cost
            players_by_cost = {}
            for player in player_pool['players']:
                cost = player['cost'].replace('$', '')
                if cost not in players_by_cost:
                    players_by_cost[cost] = []
                players_by_cost[cost].append(player)
            
            logger.info("Players grouped by cost:")
            for cost, players in players_by_cost.items():
                logger.info(f"${cost}: {len(players)} players")
            
            # Select players from each category
            for category in categories:
                players = players_by_cost.get(category, [])
                if players:
                    selected = random.sample(players, min(5, len(players)))
                    selected_players.extend(selected)
                    logger.info(f"Selected {len(selected)} players from ${category} category")
                    
            self.players = selected_players
            self.submissions = []
            
            logger.info(f"Generated challenge with {len(self.players)} total players")
            
            # Save the new challenge
            self._save_challenge()
            logger.info(f"Challenge saved for date {self.date}")
            
        except Exception as e:
            logger.error(f"Error generating new challenge: {str(e)}")
            logger.exception("Full traceback:")
            self.players = []
            self.submissions = []
            
    def _save_challenge(self):
        """Save challenge data to file"""
        try:
            os.makedirs('data/challenges', exist_ok=True)
            file_path = f"data/challenges/{self.date}.json"
            
            data = {
                'date': self.date,
                'players': self.players,
                'submissions': self.submissions
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving challenge: {str(e)}")
            
    def submit_team(self, player_name: str, team: List[Dict], record: Dict) -> bool:
        """Submit a team for the challenge"""
        try:
            # Validate team
            if len(team) != 5:
                logger.error(f"Invalid team size: {len(team)}")
                return False
                
            # Calculate total cost
            total_cost = sum(player.get('cost', 0) for player in team)
            if total_cost > 15:  # $15 budget
                logger.error(f"Team exceeds budget: ${total_cost}")
                return False
                
            # Add submission
            submission = {
                'player_name': player_name,
                'team': team,
                'record': record,
                'timestamp': datetime.now().isoformat()
            }
            
            self.submissions.append(submission)
            self._save_challenge()
            
            return True
            
        except Exception as e:
            logger.error(f"Error submitting team: {str(e)}")
            return False
            
    def get_leaderboard(self) -> List[Dict]:
        """Get the challenge leaderboard"""
        try:
            # Sort submissions by wins
            sorted_submissions = sorted(
                self.submissions,
                key=lambda x: (x['record']['wins'], -x['record']['losses']),
                reverse=True
            )
            
            return sorted_submissions
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return []
            
    def get_player_submission(self, player_name: str) -> Optional[Dict]:
        """Get a player's submission"""
        try:
            for submission in self.submissions:
                if submission['player_name'] == player_name:
                    return submission
            return None
            
        except Exception as e:
            logger.error(f"Error getting player submission: {str(e)}")
            return None
    
    def add_submission(self, player_name, team, record):
        """Add a player submission to the challenge"""
        submission = {
            'player_name': player_name,
            'team': team,
            'record': record,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.submissions.append(submission)
        self._save_challenge()
        
        return submission
    
    def calculate_percentile(self, player_name, record):
        """Calculate the percentile rank of a player's submission"""
        # Get all submissions with records
        submissions_with_records = [
            sub for sub in self.submissions 
            if 'record' in sub and isinstance(sub['record'], dict) and 'wins' in sub['record']
        ]
        
        # Add the current submission if it's not already in the list
        current_submission = {
            'player_name': player_name,
            'record': record
        }
        
        if current_submission not in submissions_with_records:
            submissions_with_records.append(current_submission)
        
        # Sort by wins (descending)
        sorted_submissions = sorted(
            submissions_with_records,
            key=lambda x: (x['record']['wins'], -x['record']['losses']),
            reverse=True
        )
        
        # Find the rank of the current submission
        total_submissions = len(sorted_submissions)
        if total_submissions <= 1:
            return 100  # If there's only one submission, it's the best
        
        # Find the index of the current submission
        for i, sub in enumerate(sorted_submissions):
            if sub['player_name'] == player_name:
                # Calculate percentile (higher is better)
                percentile = 100 - ((i / (total_submissions - 1)) * 100)
                return round(percentile, 1)
        
        return 0  # Default if not found
    
    def get_percentile_message(self, percentile):
        """Get a friendly message based on the percentile rank"""
        if percentile >= 90:
            return f"You were in the top {percentile}% of players for today's game!"
        elif percentile >= 75:
            return f"You were in the top {percentile}% of players for today's game!"
        elif percentile >= 50:
            return f"You were in the top {percentile}% of players for today's game!"
        elif percentile >= 25:
            return f"You were in the top {percentile}% of players for today's game!"
        else:
            return f"You were in the top {percentile}% of players for today's game!"
    
    def get_available_dates(self):
        """Get a list of all available challenge dates"""
        challenge_dir = 'data/challenges'
        if not os.path.exists(challenge_dir):
            return []
        
        dates = []
        for filename in os.listdir(challenge_dir):
            if filename.endswith('.json'):
                date = filename.replace('.json', '')
                dates.append(date)
        
        return sorted(dates, reverse=True)
    
    def get_challenge_by_date(self, date):
        """Get a challenge by date"""
        challenge_file = f'data/challenges/{date}.json'
        if not os.path.exists(challenge_file):
            return None
        
        with open(challenge_file, 'r') as f:
            data = json.load(f)
            return data 