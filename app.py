from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import json
from team_simulator import TeamSimulator, Player
from models import DailyChallenge
import os
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import logging
from player_pool import PlayerPool
from data_fetcher import NBADataFetcher
import time
import gc
from dotenv import load_dotenv
from gevent.pool import Pool
from player_stats import get_player_stats, get_all_player_stats, get_player_3_season_avg
from team_builder import TeamBuilder
from static_player_pool import get_static_player_pool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize connection pool
pool = Pool(100)  # Limit concurrent operations

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://budgetgm.netlify.app",
            "https://budget-gm-frontend.onrender.com",
            "http://localhost:3000",
            "https://budget-gm-frontend.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow-headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Ensure data directories exist
os.makedirs('data/challenges', exist_ok=True)
os.makedirs('cache', exist_ok=True)

# Initialize services with connection pooling
data_fetcher = NBADataFetcher()
player_pool = PlayerPool()
simulator = TeamSimulator()

# Initialize team builder and simulator
team_builder = TeamBuilder()
team_simulator = TeamSimulator()

# Cache for player pool
_player_pool_cache = None
_last_cache_update = 0
CACHE_DURATION = 3600  # 1 hour in seconds

def get_cached_player_pool():
    """Get cached player pool with time-based refresh"""
    global _player_pool_cache, _last_cache_update
    
    current_time = time.time()
    if _player_pool_cache is None or (current_time - _last_cache_update) > CACHE_DURATION:
        try:
            logger.info("Refreshing player pool cache...")
            _player_pool_cache = get_static_player_pool()
            _last_cache_update = current_time
            logger.info(f"Successfully cached {len(_player_pool_cache)} players")
        except Exception as e:
            logger.error(f"Error refreshing player pool cache: {str(e)}")
            if _player_pool_cache is None:
                raise
    
    return _player_pool_cache

@app.route('/')
def index():
    # Get the current challenge
    today = datetime.now().strftime('%Y-%m-%d')
    challenge = DailyChallenge(today)
    
    # Check if user has already submitted for today
    player_name = session.get('player_name')
    has_submitted = False
    
    if player_name:
        submission = challenge.get_player_submission(player_name)
        has_submitted = submission is not None
    
    return render_template('index.html', 
                          challenge=challenge, 
                          player_name=player_name,
                          has_submitted=has_submitted)

@app.route('/login', methods=['POST'])
def login():
    player_name = request.form.get('player_name')
    if player_name:
        session['player_name'] = player_name
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('player_name', None)
    return redirect(url_for('index'))

@app.route('/api/player-pool', methods=['GET'])
def get_player_pool():
    try:
        # Load the tiered player pool
        with open('tiered_player_pool.json', 'r') as f:
            player_pool = json.load(f)
        
        # Ensure we have exactly 5 players per tier
        for tier in ['$5', '$4', '$3', '$2', '$1']:
            if len(player_pool[tier]) != 5:
                raise ValueError(f"Expected 5 players in {tier} tier, got {len(player_pool[tier])}")
        
        return jsonify(player_pool)
    except Exception as e:
        logger.error(f"Error getting player pool: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team', methods=['POST'])
def create_team():
    try:
        data = request.get_json()
        if not data or 'players' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        team = TeamBuilder()
        for player in data['players']:
            if not team.add_player(player):
                return jsonify({'error': f'Failed to add player {player}'}), 400
                
        return jsonify(team.get_team_summary())
    except Exception as e:
        logger.error(f"Error in create_team: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate', methods=['POST'])
def simulate_game():
    try:
        data = request.get_json()
        if not data or 'team1' not in data or 'team2' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        result = team_simulator.simulate_game(data['team1'], data['team2'])
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in simulate_game: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<player_name>', methods=['GET'])
def get_player(player_name):
    try:
        player_data = get_player_stats(player_name)
        if not player_data:
            return jsonify({'error': 'Player not found'}), 404
        return jsonify(player_data)
    except Exception as e:
        logger.error(f"Error in get_player: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate-team', methods=['POST'])
def simulate_team():
    try:
        data = request.get_json()
        if not data or 'players' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        # Create team simulator
        team = TeamSimulator()
        
        # Add players to team
        for player_data in data['players']:
            try:
                player = Player(
                    name=player_data['name'],
                    stats=player_data['stats']
                )
                team.add_player(player)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
        # Simulate season
        wins, losses = team.simulate_season()
        
        return jsonify({
            'wins': wins,
            'losses': losses,
            'win_probability': team.win_probability,
            'team_stats': team.get_team_stats()
        })
        
    except Exception as e:
        logger.error(f"Error simulating team: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        # Force garbage collection
        gc.collect()

@app.route('/api/validate-team', methods=['POST'])
def validate_team():
    try:
        data = request.get_json()
        if not data or 'players' not in data:
            return jsonify({'error': 'No players provided'}), 400
        
        # Load the tiered player pool
        with open('tiered_player_pool.json', 'r') as f:
            player_pool = json.load(f)
        
        # Validate each player exists in the pool
        total_cost = 0
        for player in data['players']:
            found = False
            for tier in ['$5', '$4', '$3', '$2', '$1']:
                if any(p['name'] == player['name'] for p in player_pool[tier]):
                    total_cost += int(tier.replace('$', ''))
                    found = True
                    break
            if not found:
                return jsonify({'error': f'Player {player["name"]} not found in pool'}), 400
        
        # Check budget constraint
        if total_cost > 15:
            return jsonify({'error': f'Team cost ${total_cost} exceeds budget of $15'}), 400
        
        # Check minimum players
        if len(data['players']) < 5:
            return jsonify({'error': 'Team must have at least 5 players'}), 400
        
        return jsonify({
            'valid': True,
            'total_cost': total_cost,
            'remaining_budget': 15 - total_cost
        })
    except Exception as e:
        logger.error(f"Error validating team: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/leaderboard')
def leaderboard():
    # Check if a date parameter is provided
    date = request.args.get('date')
    
    if date:
        # Load the challenge for the specified date
        challenge = DailyChallenge(date)
    else:
        # Get the current challenge
        today = datetime.now().strftime('%Y-%m-%d')
        challenge = DailyChallenge(today)
    
    leaderboard_data = challenge.get_leaderboard()
    
    player_name = session.get('player_name')
    player_rank = None
    player_percentile = None
    
    if player_name:
        for i, submission in enumerate(leaderboard_data):
            if submission['player_name'] == player_name:
                player_rank = i + 1
                player_percentile = submission.get('percentile', 0)
                break
    
    return render_template('leaderboard.html', 
                          leaderboard=leaderboard_data,
                          player_name=player_name,
                          player_rank=player_rank,
                          player_percentile=player_percentile,
                          challenge_date=challenge.date)

@app.route('/api/check_submission')
def check_submission():
    player_name = request.args.get('player_name')
    date = request.args.get('date')  # Optional date parameter
    
    if not player_name:
        return jsonify({'error': 'Missing player name'}), 400
    
    # Get the challenge for the specified date or today
    today = datetime.now().strftime('%Y-%m-%d')
    challenge = DailyChallenge(date) if date else DailyChallenge(today)
    
    submission = challenge.get_player_submission(player_name)
    return jsonify({
        'has_submission': submission is not None,
        'submission': submission
    })

@app.route('/api/submitted_team')
def get_submitted_team():
    player_name = request.args.get('player_name')
    date = request.args.get('date')  # Optional date parameter
    
    if not player_name:
        return jsonify({'error': 'Missing player name'}), 400
    
    # Get the challenge for the specified date or today
    today = datetime.now().strftime('%Y-%m-%d')
    challenge = DailyChallenge(date) if date else DailyChallenge(today)
    
    submission = challenge.get_player_submission(player_name)
    if not submission:
        return jsonify({'error': 'No submission found'}), 404
    
    return jsonify(submission)

@app.route('/api/available_dates')
def get_available_dates():
    challenge = DailyChallenge(datetime.now().strftime('%Y-%m-%d'))
    dates = challenge.get_available_dates()
    return jsonify(dates)

@app.route('/api/challenge/<date>')
def get_challenge_by_date(date):
    challenge = DailyChallenge(date)
    if not challenge.players:
        return jsonify({'error': 'Challenge not found'}), 404
    
    return jsonify({
        'date': challenge.date,
        'players': challenge.players
    })

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all players with their stats"""
    try:
        players = get_all_player_stats()
        return jsonify({
            'success': True,
            'data': players
        })
    except Exception as e:
        logger.error(f"Error getting players: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/players/<player_name>/stats', methods=['GET'])
def get_player_stats_endpoint(player_name: str):
    """Get current and 3-season average stats for a player"""
    try:
        current_stats = get_player_stats(player_name)
        three_season_avg = get_player_3_season_avg(player_name)
        
        if not current_stats or not three_season_avg:
            return jsonify({
                'success': False,
                'error': f"Stats not found for player {player_name}"
            }), 404
            
        return jsonify({
            'success': True,
            'data': {
                'current': current_stats['stats'],
                'three_season_avg': three_season_avg
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats for {player_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/simulate/season', methods=['POST'])
def simulate_season():
    try:
        data = request.get_json()
        if not data or 'players' not in data:
            return jsonify({'error': 'No players provided'}), 400
        
        # Load the tiered player pool to get full player stats
        with open('tiered_player_pool.json', 'r') as f:
            player_pool = json.load(f)
        
        # Get full player data for each selected player
        selected_players = []
        for player in data['players']:
            # Find the player in our pool
            for tier in ['$5', '$4', '$3', '$2', '$1']:
                found_player = next((p for p in player_pool[tier] if p['name'] == player['name']), None)
                if found_player:
                    selected_players.append(found_player)
                    break
        
        if len(selected_players) != len(data['players']):
            return jsonify({'error': 'Could not find all selected players in the pool'}), 400
        
        # Simulate the season
        simulator = TeamSimulator()
        results = simulator.simulate_season(selected_players)
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error simulating season: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/stats/summary/<player_name>', methods=['GET'])
def get_player_stats_summary(player_name: str):
    """Get a comprehensive stats summary for a player"""
    try:
        summary = simulator.get_player_stats_summary(player_name)
        if not summary:
            return jsonify({
                'success': False,
                'error': f"Stats summary not found for player {player_name}"
            }), 404
            
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error getting stats summary for {player_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 