import random
from flask import Flask, request, jsonify, session, render_template
from game_logic.account import load_account, save_balance, get_balance, get_username, set_username, get_leaderboard
from game_logic.ride_the_bus import (
    new_game, evaluate_guess, cash_out,
    get_phase_question, get_multiplier, visible_cards
)
from game_logic.social import (
    send_message, get_messages, CHAT_COST, DM_COST,
    send_dm, get_dms, find_player_by_username,
    touch_activity, search_users,
    buy_ticket, get_lottery_info, check_and_draw, get_player_tickets, TICKET_COST,
    register_active_game, update_active_game, remove_active_game,
    get_active_games, place_side_bet, resolve_side_bets, get_my_side_bets,
)

import time as _time

app = Flask(__name__)
app.secret_key = 'rtb-secret-key-change-in-prod'

# Spam limiter: tracks recent message timestamps per player
_chat_history = {}  # player_id -> list of timestamps
_chat_cooldown = {}  # player_id -> cooldown expiry timestamp
SPAM_WINDOW = 1  # seconds
SPAM_LIMIT = 5  # max messages in window
SPAM_COOLDOWN = 15  # seconds to pause

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
    touch_activity(player_id)
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

    # Register as active game for side betting
    username = get_username(player_id)
    if username:
        register_active_game(player_id, username, bet)

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

    # Update active game phase for side-bet viewers
    if state['status'] == 'active':
        update_active_game(player_id, state['phase'])

    # If the game just ended, handle payouts
    if state['status'] == 'won':
        balance += state['payout']
        save_balance(player_id, balance)
        resolve_side_bets(player_id, 'win', win_multiplier=20)
        remove_active_game(player_id)
    elif state['status'] == 'lost':
        resolve_side_bets(player_id, 'bust')
        remove_active_game(player_id)
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

    # Withdrawal counts as 'win' for side-bet purposes
    # Use the multiplier the player cashed out at
    withdraw_mult = get_multiplier(state['phase'] - 1) if state['phase'] > 0 else 1
    resolve_side_bets(player_id, 'win', win_multiplier=withdraw_mult)
    remove_active_game(player_id)

    return jsonify({
        'balance': balance,
        'cards': visible_cards(state),
        'log': state['log'],
        'status': state['status'],
        'payout': state['payout'],
    })


# ---------- Chat API ----------

@app.route('/api/chat', methods=['GET'])
def api_chat_get():
    """Get recent chat messages visible to this player."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify([])  
    touch_activity(player_id)
    return jsonify(get_messages(player_id, 50))


@app.route('/api/chat', methods=['POST'])
def api_chat_post():
    """Send a chat message. Free for public, 50 chips for @mentions."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400

    username = get_username(player_id)
    if not username:
        return jsonify({'error': 'Set a username first'}), 400

    data = request.get_json()
    content = data.get('message', '').strip()
    if not content or len(content) > 200:
        return jsonify({'error': 'Message must be 1-200 characters'}), 400

    touch_activity(player_id)

    # Spam limiter
    now = _time.time()
    if player_id in _chat_cooldown and now < _chat_cooldown[player_id]:
        remaining = int(_chat_cooldown[player_id] - now)
        return jsonify({'error': f'Slow down! Chat paused for {remaining}s'}), 429

    history = _chat_history.get(player_id, [])
    history = [t for t in history if now - t < SPAM_WINDOW]
    history.append(now)
    _chat_history[player_id] = history
    if len(history) > SPAM_LIMIT:
        _chat_cooldown[player_id] = now + SPAM_COOLDOWN
        return jsonify({'error': f'Too many messages! Chat paused for {SPAM_COOLDOWN}s'}), 429

    # Check if it's a private @mention
    recipient_id = None
    recipient_username = None
    if content.startswith('@'):
        parts = content.split(' ', 1)
        target_name = parts[0][1:]  # strip the @
        msg_body = parts[1] if len(parts) > 1 else ''
        if not msg_body:
            return jsonify({'error': 'Add a message after @username'}), 400
        recipient_id = find_player_by_username(target_name)
        if not recipient_id:
            return jsonify({'error': f'User "{target_name}" not found'}), 404
        if recipient_id == player_id:
            return jsonify({'error': "Can't DM yourself"}), 400
        recipient_username = target_name
        # Charge DM cost
        balance = get_balance(player_id)
        if balance < DM_COST:
            return jsonify({'error': f'Need {DM_COST} chips to send a private message'}), 400
        save_balance(player_id, balance - DM_COST)
        content = msg_body  # store only the message body

    msg = send_message(player_id, username, content, recipient_id, recipient_username)
    return jsonify({'message': msg, 'balance': get_balance(player_id)})


@app.route('/api/users/search', methods=['GET'])
def api_user_search():
    """Search usernames by prefix for autocomplete."""
    player_id = session.get('player_id')
    prefix = request.args.get('q', '').strip()
    if not prefix:
        return jsonify([])
    return jsonify(search_users(prefix, exclude_player=player_id, limit=8))


# ---------- DM API ----------

@app.route('/api/dms', methods=['GET'])
def api_dms_get():
    """Get the current player's DMs."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400
    return jsonify(get_dms(player_id, 50))


@app.route('/api/dms', methods=['POST'])
def api_dms_post():
    """Send a DM. Costs 50 chips."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400

    username = get_username(player_id)
    if not username:
        return jsonify({'error': 'Set a username first'}), 400

    data = request.get_json()
    recipient = data.get('to', '').strip()
    content = data.get('message', '').strip()

    if not recipient:
        return jsonify({'error': 'Specify a recipient username'}), 400
    if not content or len(content) > 200:
        return jsonify({'error': 'Message must be 1-200 characters'}), 400

    recipient_id = find_player_by_username(recipient)
    if not recipient_id:
        return jsonify({'error': f'User "{recipient}" not found'}), 404
    if recipient_id == player_id:
        return jsonify({'error': "Can't DM yourself"}), 400

    balance = get_balance(player_id)
    if balance < DM_COST:
        return jsonify({'error': f'Need {DM_COST} chips to send a DM'}), 400

    save_balance(player_id, balance - DM_COST)
    msg = send_dm(player_id, username, recipient_id, recipient, content)
    return jsonify({'message': msg, 'balance': balance - DM_COST})


# ---------- Lottery API ----------

@app.route('/api/lottery', methods=['GET'])
def api_lottery_info():
    """Get current lottery state."""
    player_id = session.get('player_id')
    # Check if a draw is due
    draw_result = check_and_draw()
    info = get_lottery_info()
    if player_id:
        info['my_tickets'] = get_player_tickets(player_id)
    else:
        info['my_tickets'] = 0
    if draw_result:
        info['just_drawn'] = draw_result
    return jsonify(info)


@app.route('/api/lottery/buy', methods=['POST'])
def api_lottery_buy():
    """Buy a lottery ticket. Costs 100 chips."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400

    username = get_username(player_id)
    if not username:
        return jsonify({'error': 'Set a username first'}), 400

    balance = get_balance(player_id)
    if balance < TICKET_COST:
        return jsonify({'error': f'Need {TICKET_COST} chips for a ticket'}), 400

    save_balance(player_id, balance - TICKET_COST)
    count = buy_ticket(player_id, username)
    return jsonify({'balance': balance - TICKET_COST, 'my_tickets': count})


# ---------- Side Bets API ----------

@app.route('/api/active-games', methods=['GET'])
def api_active_games():
    """Get list of players currently in a game."""
    player_id = session.get('player_id')
    games = get_active_games(exclude_player=player_id)
    return jsonify(games)


@app.route('/api/side-bet', methods=['POST'])
def api_side_bet():
    """Place a side bet on another player's game."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400

    username = get_username(player_id)
    if not username:
        return jsonify({'error': 'Set a username first'}), 400

    data = request.get_json()
    target_id = data.get('target_id', '')
    amount = data.get('amount', 0)
    prediction = data.get('prediction', '')

    if prediction not in ('win', 'bust'):
        return jsonify({'error': 'Prediction must be win or bust'}), 400
    if not isinstance(amount, int) or amount < 50:
        return jsonify({'error': 'Minimum side bet is 50 chips'}), 400

    balance = get_balance(player_id)
    if balance < amount:
        return jsonify({'error': 'Not enough chips'}), 400

    # Get target username
    target_username = get_username(target_id)
    if not target_username:
        return jsonify({'error': 'Player not found'}), 400

    save_balance(player_id, balance - amount)
    place_side_bet(player_id, username, target_id, target_username, amount, prediction)
    return jsonify({'balance': balance - amount})


@app.route('/api/my-side-bets', methods=['GET'])
def api_my_side_bets():
    """Get the current player's active side bets."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'No session'}), 400
    return jsonify(get_my_side_bets(player_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
