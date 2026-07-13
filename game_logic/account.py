import sqlite3
import os
import random
import string

DB_PATH = os.environ.get('DB_PATH', '/data/accounts.db')
STARTING_BALANCE = 5000

def _get_conn():
    """Open a connection to the SQLite database and ensure the accounts table exists."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            player_id TEXT PRIMARY KEY,
            balance   INTEGER NOT NULL,
            username  TEXT UNIQUE
        )
    ''')
    conn.commit()
    # Migrate older databases that lack the username column
    try:
        conn.execute('ALTER TABLE accounts ADD COLUMN username TEXT UNIQUE')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    return conn

def generate_id():
    """Generate a random unique player ID."""
    chars = string.ascii_lowercase + string.digits
    return 'player-' + ''.join(random.choices(chars, k=12))

def load_account(player_id=None):
    """
    Load an existing account by player_id, or create a new one.
    Returns (player_id, balance).
    """
    conn = _get_conn()
    if player_id:
        row = conn.execute(
            'SELECT player_id, balance FROM accounts WHERE player_id = ?', (player_id,)
        ).fetchone()
        if row:
            conn.close()
            return row[0], row[1]
        # Player ID exists in cookie but not in DB (e.g. DB was wiped) - restore it
        conn.execute('INSERT INTO accounts (player_id, balance) VALUES (?, ?)', (player_id, STARTING_BALANCE))
        conn.commit()
        conn.close()
        return player_id, STARTING_BALANCE
    # Brand new visitor - generate a fresh ID
    new_id = generate_id()
    conn.execute('INSERT INTO accounts (player_id, balance) VALUES (?, ?)', (new_id, STARTING_BALANCE))
    conn.commit()
    conn.close()
    return new_id, STARTING_BALANCE

def save_balance(player_id, balance):
    """Persist the player's current balance to the database."""
    conn = _get_conn()
    conn.execute('UPDATE accounts SET balance = ? WHERE player_id = ?', (balance, player_id))
    conn.commit()
    conn.close()

def get_balance(player_id):
    """Fetch the current balance for a player. Returns None if player not found."""
    conn = _get_conn()
    row = conn.execute(
        'SELECT balance FROM accounts WHERE player_id = ?', (player_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else None

def get_username(player_id):
    """Fetch the username for a player. Returns None if not set."""
    conn = _get_conn()
    row = conn.execute(
        'SELECT username FROM accounts WHERE player_id = ?', (player_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else None

def set_username(player_id, username):
    """
    Assign a username to a player.
    Returns True on success, False if the username is already taken.
    """
    conn = _get_conn()
    try:
        conn.execute('UPDATE accounts SET username = ? WHERE player_id = ?', (username, player_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_leaderboard(limit=10):
    """Return the top players by balance. Only includes players with a username."""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT username, balance FROM accounts WHERE username IS NOT NULL ORDER BY balance DESC LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    return [{'username': r[0], 'balance': r[1]} for r in rows]
