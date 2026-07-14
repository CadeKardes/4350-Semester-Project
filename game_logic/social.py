import sqlite3
import os
import time
import random

DB_PATH = os.environ.get('DB_PATH', '/data/accounts.db')

def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Chat messages table (recipient_id is NULL for public, set for @mentions)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            recipient_id TEXT,
            recipient_username TEXT,
            timestamp REAL NOT NULL
        )
    ''')

    # Migrate: add recipient columns if missing
    try:
        conn.execute('ALTER TABLE chat_messages ADD COLUMN recipient_id TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE chat_messages ADD COLUMN recipient_username TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Online status tracking
    conn.execute('''
        CREATE TABLE IF NOT EXISTS player_activity (
            player_id TEXT PRIMARY KEY,
            last_active REAL NOT NULL
        )
    ''')

    # Lottery tickets table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS lottery_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            username TEXT NOT NULL,
            purchased_at REAL NOT NULL
        )
    ''')

    # Lottery draws history
    conn.execute('''
        CREATE TABLE IF NOT EXISTS lottery_draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner_id TEXT,
            winner_username TEXT,
            pot INTEGER NOT NULL,
            drawn_at REAL NOT NULL
        )
    ''')

    # Side bets on active games
    conn.execute('''
        CREATE TABLE IF NOT EXISTS side_bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bettor_id TEXT NOT NULL,
            bettor_username TEXT NOT NULL,
            target_id TEXT NOT NULL,
            target_username TEXT NOT NULL,
            amount INTEGER NOT NULL,
            prediction TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            placed_at REAL NOT NULL
        )
    ''')

    # Direct messages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS direct_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT NOT NULL,
            sender_username TEXT NOT NULL,
            recipient_id TEXT NOT NULL,
            recipient_username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    ''')

    # Active games registry (so others can see who's playing)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS active_games (
            player_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            bet INTEGER NOT NULL,
            phase INTEGER NOT NULL DEFAULT 0,
            started_at REAL NOT NULL
        )
    ''')

    conn.commit()
    return conn


# ===================== CHAT =====================

CHAT_COST = 0  # global chat is free
DM_COST = 50  # chips per @mention (private message)

def send_message(player_id, username, content, recipient_id=None, recipient_username=None):
    """Store a chat message. If recipient_id is set, it's a private @mention."""
    conn = _get_conn()
    ts = time.time()
    conn.execute(
        'INSERT INTO chat_messages (player_id, username, content, recipient_id, recipient_username, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (player_id, username, content, recipient_id, recipient_username, ts)
    )
    conn.commit()
    conn.close()
    return {'username': username, 'content': content, 'recipient': recipient_username, 'timestamp': ts, 'private': recipient_id is not None}


def get_messages(player_id, limit=50):
    """Fetch messages visible to this player: all public + private where they are sender or recipient."""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT username, content, recipient_username, player_id, recipient_id, timestamp FROM chat_messages '
        'WHERE recipient_id IS NULL OR player_id = ? OR recipient_id = ? '
        'ORDER BY id DESC LIMIT ?',
        (player_id, player_id, limit)
    ).fetchall()
    conn.close()
    # Return in chronological order
    return [{
        'username': r[0],
        'content': r[1],
        'recipient': r[2],
        'private': r[3] == player_id or r[4] == player_id if r[4] else False,
        'is_private': r[4] is not None,
        'timestamp': r[5]
    } for r in reversed(rows)]


# ===================== ONLINE STATUS =====================

ONLINE_THRESHOLD = 60  # seconds - player is "online" if active within this window

def touch_activity(player_id):
    """Update a player's last_active timestamp."""
    conn = _get_conn()
    conn.execute(
        'INSERT OR REPLACE INTO player_activity (player_id, last_active) VALUES (?, ?)',
        (player_id, time.time())
    )
    conn.commit()
    conn.close()


def search_users(prefix, exclude_player=None, limit=10):
    """Search for usernames starting with prefix. Returns list with online/offline status."""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT a.player_id, a.username, p.last_active FROM accounts a '
        'LEFT JOIN player_activity p ON a.player_id = p.player_id '
        'WHERE a.username IS NOT NULL AND a.username LIKE ? '
        'ORDER BY a.username ASC LIMIT ?',
        (prefix + '%', limit)
    ).fetchall()
    conn.close()
    now = time.time()
    results = []
    for r in rows:
        if exclude_player and r[0] == exclude_player:
            continue
        online = r[2] is not None and (now - r[2]) < ONLINE_THRESHOLD
        results.append({'username': r[1], 'online': online})
    return results


# ===================== DIRECT MESSAGES =====================

def send_dm(sender_id, sender_username, recipient_id, recipient_username, content):
    """Store a direct message. Returns the message dict."""
    conn = _get_conn()
    ts = time.time()
    conn.execute(
        'INSERT INTO direct_messages (sender_id, sender_username, recipient_id, recipient_username, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
        (sender_id, sender_username, recipient_id, recipient_username, content, ts)
    )
    conn.commit()
    conn.close()
    return {'from': sender_username, 'to': recipient_username, 'content': content, 'timestamp': ts}


def get_dms(player_id, limit=50):
    """Fetch DMs sent to or from a player."""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT sender_username, recipient_username, content, timestamp FROM direct_messages '
        'WHERE sender_id = ? OR recipient_id = ? ORDER BY id DESC LIMIT ?',
        (player_id, player_id, limit)
    ).fetchall()
    conn.close()
    return [{'from': r[0], 'to': r[1], 'content': r[2], 'timestamp': r[3]} for r in reversed(rows)]


def find_player_by_username(username):
    """Look up a player_id by username. Returns player_id or None."""
    conn = _get_conn()
    row = conn.execute(
        'SELECT player_id FROM accounts WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return row[0] if row else None


# ===================== LOTTERY =====================

TICKET_COST = 100  # chips per ticket
DRAW_INTERVAL = 86400  # 24 hours in seconds

def buy_ticket(player_id, username):
    """Buy a lottery ticket. Returns ticket count for this player."""
    conn = _get_conn()
    conn.execute(
        'INSERT INTO lottery_tickets (player_id, username, purchased_at) VALUES (?, ?, ?)',
        (player_id, username, time.time())
    )
    conn.commit()
    count = conn.execute(
        'SELECT COUNT(*) FROM lottery_tickets WHERE player_id = ?', (player_id,)
    ).fetchone()[0]
    conn.close()
    return count


def get_lottery_info():
    """Get current lottery state: pot, ticket count, last winner, time until draw."""
    conn = _get_conn()

    # Current tickets and pot
    ticket_count = conn.execute('SELECT COUNT(*) FROM lottery_tickets').fetchone()[0]
    pot = ticket_count * TICKET_COST

    # Last draw
    last_draw = conn.execute(
        'SELECT winner_username, pot, drawn_at FROM lottery_draws ORDER BY id DESC LIMIT 1'
    ).fetchone()

    # Determine next draw time
    if last_draw:
        next_draw = last_draw[2] + DRAW_INTERVAL
    else:
        # If no draw has ever happened, next draw is DRAW_INTERVAL from first ticket or now
        first_ticket = conn.execute(
            'SELECT purchased_at FROM lottery_tickets ORDER BY id ASC LIMIT 1'
        ).fetchone()
        if first_ticket:
            next_draw = first_ticket[0] + DRAW_INTERVAL
        else:
            next_draw = time.time() + DRAW_INTERVAL

    conn.close()

    return {
        'pot': pot,
        'ticket_count': ticket_count,
        'ticket_cost': TICKET_COST,
        'last_winner': last_draw[0] if last_draw else None,
        'last_pot': last_draw[1] if last_draw else 0,
        'next_draw': next_draw,
        'time_left': max(0, next_draw - time.time()),
    }


def check_and_draw():
    """Check if it's time to draw. If so, pick a winner and reset. Returns winner info or None."""
    conn = _get_conn()

    ticket_count = conn.execute('SELECT COUNT(*) FROM lottery_tickets').fetchone()[0]
    if ticket_count == 0:
        conn.close()
        return None

    # Check if draw is due
    last_draw = conn.execute(
        'SELECT drawn_at FROM lottery_draws ORDER BY id DESC LIMIT 1'
    ).fetchone()

    if last_draw:
        next_draw = last_draw[0] + DRAW_INTERVAL
    else:
        first_ticket = conn.execute(
            'SELECT purchased_at FROM lottery_tickets ORDER BY id ASC LIMIT 1'
        ).fetchone()
        next_draw = first_ticket[0] + DRAW_INTERVAL if first_ticket else time.time() + DRAW_INTERVAL

    if time.time() < next_draw:
        conn.close()
        return None

    # Time to draw! Pick a random ticket
    pot = ticket_count * TICKET_COST
    winner_row = conn.execute(
        'SELECT player_id, username FROM lottery_tickets ORDER BY RANDOM() LIMIT 1'
    ).fetchone()

    winner_id = winner_row[0]
    winner_username = winner_row[1]

    # Record the draw
    conn.execute(
        'INSERT INTO lottery_draws (winner_id, winner_username, pot, drawn_at) VALUES (?, ?, ?, ?)',
        (winner_id, winner_username, pot, time.time())
    )

    # Clear all tickets
    conn.execute('DELETE FROM lottery_tickets')

    # Add winnings to winner's balance
    conn.execute(
        'UPDATE accounts SET balance = balance + ? WHERE player_id = ?',
        (pot, winner_id)
    )

    conn.commit()
    conn.close()

    return {'winner': winner_username, 'pot': pot}


def get_player_tickets(player_id):
    """Get how many tickets a player currently has."""
    conn = _get_conn()
    count = conn.execute(
        'SELECT COUNT(*) FROM lottery_tickets WHERE player_id = ?', (player_id,)
    ).fetchone()[0]
    conn.close()
    return count


# ===================== GAMBLING ON OTHERS =====================

def register_active_game(player_id, username, bet):
    """Register that a player has started a game (visible to others)."""
    conn = _get_conn()
    conn.execute('''
        INSERT OR REPLACE INTO active_games (player_id, username, bet, phase, started_at)
        VALUES (?, ?, ?, 0, ?)
    ''', (player_id, username, bet, time.time()))
    conn.commit()
    conn.close()


def update_active_game(player_id, phase):
    """Update the phase of an active game."""
    conn = _get_conn()
    conn.execute('UPDATE active_games SET phase = ? WHERE player_id = ?', (phase, player_id))
    conn.commit()
    conn.close()


def remove_active_game(player_id):
    """Remove a player from active games (game ended)."""
    conn = _get_conn()
    conn.execute('DELETE FROM active_games WHERE player_id = ?', (player_id,))
    conn.commit()
    conn.close()


def get_active_games(exclude_player=None):
    """Get list of currently active games (excludes the requesting player)."""
    conn = _get_conn()
    if exclude_player:
        rows = conn.execute(
            'SELECT player_id, username, bet, phase, started_at FROM active_games WHERE player_id != ? ORDER BY started_at DESC',
            (exclude_player,)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT player_id, username, bet, phase, started_at FROM active_games ORDER BY started_at DESC'
        ).fetchall()
    conn.close()
    return [{'player_id': r[0], 'username': r[1], 'bet': r[2], 'phase': r[3]} for r in rows]


def place_side_bet(bettor_id, bettor_username, target_id, target_username, amount, prediction):
    """
    Place a side bet on another player's game.
    prediction: 'win' (they complete all 4) or 'bust' (they lose before finishing)
    """
    conn = _get_conn()
    conn.execute('''
        INSERT INTO side_bets (bettor_id, bettor_username, target_id, target_username, amount, prediction, status, placed_at)
        VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
    ''', (bettor_id, bettor_username, target_id, target_username, amount, prediction, time.time()))
    conn.commit()
    conn.close()


def resolve_side_bets(target_id, outcome, win_multiplier=2):
    """
    Resolve all active side bets on a target player.
    outcome: 'win' if they completed all 4 rounds or withdrew, 'bust' if they lost.
    win_multiplier: the game multiplier the target player achieved (used for 'win' bets).
    'bust' bets pay 1.5x since losing is more likely.
    Returns list of (bettor_id, payout) for winners.
    """
    conn = _get_conn()
    bets = conn.execute(
        'SELECT id, bettor_id, amount, prediction FROM side_bets WHERE target_id = ? AND status = ?',
        (target_id, 'active')
    ).fetchall()

    payouts = []
    for bet_id, bettor_id, amount, prediction in bets:
        if prediction == outcome:
            if prediction == 'win':
                payout = int(amount * win_multiplier)
            else:
                payout = int(amount * 1.5)
            conn.execute('UPDATE accounts SET balance = balance + ? WHERE player_id = ?', (payout, bettor_id))
            payouts.append((bettor_id, payout))
            conn.execute('UPDATE side_bets SET status = ? WHERE id = ?', ('won', bet_id))
        else:
            conn.execute('UPDATE side_bets SET status = ? WHERE id = ?', ('lost', bet_id))

    conn.commit()
    conn.close()
    return payouts


def get_my_side_bets(player_id):
    """Get active side bets placed by a player."""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT target_username, amount, prediction FROM side_bets WHERE bettor_id = ? AND status = ? ORDER BY placed_at DESC',
        (player_id, 'active')
    ).fetchall()
    conn.close()
    return [{'target': r[0], 'amount': r[1], 'prediction': r[2]} for r in rows]
