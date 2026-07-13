import random
from flask import Flask, request, jsonify, session, render_template
from game_logic.account import load_account, save_balance, get_balance, get_username, set_username, get_leaderboard
from game_logic.ride_the_bus import (
    new_game, evaluate_guess, cash_out,
    get_phase_question, get_multiplier, visible_cards
)

app = Flask(__name__)
app.secret_key = 'rtb-secret-key-change-in-prod'

PITY_MESSAGES = [
    "Your grandma called. She said she's disappointed in your life choices, but she slipped 100 chips in a birthday card anyway.",
    "You checked your old jacket pocket and found a crumpled 100-chip voucher from 2019. Still valid apparently.",
    "A pigeon dropped 100 chips on your head. You don't know where it came from. You don't ask questions.",
    "The casino felt so bad watching you lose that they handed you 100 chips out of pity. The dealer wouldn't make eye contact.",
    "You sold your watch for 100 chips. It wasn't even a nice watch. Here we go again.",
]


# ---------- HTML pages ----------

@app.route('/')
def index():
    """Load or create the player account and serve the game page."""
    player_id = session.get('player_id')
    player_id, balance = load_account(player_id)
    session['player_id'] = player_id
    username = get_username(player_id)
    return render_template('ride_the_bus.html', player_id=player_id, balance=balance, username=username)


# ---------- Account API ----------

@app.route('/api/register', methods=['POST'])
def api_register():
    """Set a username for the current player. Must be unique."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400

    data = request.get_json()
    username = data.get('username', '').strip()

    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters.'}), 400
    if len(username) > 20:
        return jsonify({'error': 'Username must be 20 characters or less.'}), 400
    if not username.isalnum():
        return jsonify({'error': 'Username must be letters and numbers only.'}), 400

    success = set_username(player_id, username)
    if not success:
        return jsonify({'error': 'That username is already taken.'}), 409

    return jsonify({'username': username})


@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    """Return the top 10 players by balance."""
    return jsonify(get_leaderboard(10))


@app.route('/api/account', methods=['GET'])
def api_account():
    """Return the current player's ID and balance."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400
    balance = get_balance(player_id)
    return jsonify({'player_id': player_id, 'balance': balance})


# ---------- Game API ----------

@app.route('/api/bet', methods=['POST'])
def api_bet():
    """
    Place a bet and start a new game.
    Expects JSON: { "bet": <int> }
    Returns the initial game state.
    """
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400

    data = request.get_json()
    bet = data.get('bet', 0)
    balance = get_balance(player_id)

    if not isinstance(bet, int) or bet < 1:
        return jsonify({'error': 'Enter a valid bet.'}), 400
    if bet > balance:
        return jsonify({'error': "You don't have enough chips!"}), 400

    # Deduct the bet immediately
    balance -= bet
    save_balance(player_id, balance)

    # Build a new game state and store it in the session
    state = new_game(bet)
    session['game'] = state

    return jsonify({
        'balance': balance,
        'phase': state['phase'],
        'question': get_phase_question(state['phase']),
        'multiplier': get_multiplier(state['phase']),
        'cards': visible_cards(state),
        'log': state['log'],
        'status': state['status'],
    })


@app.route('/api/guess', methods=['POST'])
def api_guess():
    """
    Submit a guess for the current phase.
    Expects JSON: { "guess": <str> }
    Returns the updated game state.
    """
    player_id = session.get('player_id')
    state = session.get('game')
    if not player_id or not state:
        return jsonify({'error': 'No active game'}), 400

    guess = request.get_json().get('guess', '')
    state = evaluate_guess(state, guess)
    session['game'] = state

    balance = get_balance(player_id)
    pity_msg = None

    # If the game just ended, handle payouts
    if state['status'] == 'won':
        balance += state['payout']
        save_balance(player_id, balance)
    elif state['status'] == 'lost':
        if balance <= 0:
            pity_msg = random.choice(PITY_MESSAGES)
            balance = 100
            save_balance(player_id, balance)

    return jsonify({
        'balance': balance,
        'phase': state['phase'],
        'question': get_phase_question(state['phase']) if state['status'] == 'active' else '',
        'multiplier': get_multiplier(state['phase']) if state['status'] == 'active' else 0,
        'prev_multiplier': get_multiplier(state['phase'] - 1) if state['phase'] > 0 else 0,
        'potential': state['bet'] * get_multiplier(state['phase'] - 1) if state['phase'] > 0 else 0,
        'cards': visible_cards(state),
        'log': state['log'],
        'status': state['status'],
        'payout': state['payout'],
        'pity_msg': pity_msg,
    })


@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    """
    Cash out at the current phase's multiplier.
    Only valid after at least one correct guess.
    """
    player_id = session.get('player_id')
    state = session.get('game')
    if not player_id or not state:
        return jsonify({'error': 'No active game'}), 400
    if state['phase'] == 0:
        return jsonify({'error': 'Nothing to withdraw yet'}), 400

    state = cash_out(state)
    session['game'] = state

    balance = get_balance(player_id)
    balance += state['payout']
    save_balance(player_id, balance)

    return jsonify({
        'balance': balance,
        'cards': visible_cards(state),
        'log': state['log'],
        'status': state['status'],
        'payout': state['payout'],
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
