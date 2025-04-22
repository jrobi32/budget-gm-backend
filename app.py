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
        # Use connection pool for data fetching
        def fetch_players():
            players = data_fetcher.get_active_players()
            if not players:
                return {'error': 'Failed to fetch players'}, 500
                
            # Get player stats in batches with pooling
            player_stats = []
            batch_size = 50
            
            def process_batch(batch):
                try:
                    stats = data_fetcher.get_player_stats(batch)
                    return stats
                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
                    return []
            
            # Process batches in parallel using the connection pool
            batches = [players[i:i + batch_size] for i in range(0, len(players), batch_size)]
            results = pool.map(process_batch, batches)
            
            # Combine results
            for batch_stats in results:
                player_stats.extend(batch_stats)
            
            if not player_stats:
                return {'error': 'Failed to fetch player stats'}, 500
                
            # Cache the results
            cache_file = os.path.join('cache', 'player_pool.json')
            with open(cache_file, 'w') as f:
                json.dump(player_stats, f)
                
            return player_stats
            
        # Check cache first
        cache_file = os.path.join('cache', 'player_pool.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return jsonify(json.load(f))
                
        # Fetch new data if cache miss
        result = fetch_players()
        if isinstance(result, tuple):  # Error case
            return jsonify(result[0]), result[1]
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_player_pool: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Force garbage collection
        gc.collect()

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
                
        return jsonify({
            'is_valid': team.is_team_valid(),
            'total_cost': team.get_team_cost(),
            'remaining_budget': team.get_remaining_budget(),
            'is_complete': team.is_team_complete()
        })
        
    except Exception as e:
        logger.error(f"Error validating team: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        # Force garbage collection
        gc.collect()

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 