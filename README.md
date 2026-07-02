# Ride the Bus

A retro pixel-art card gambling game built with Flask and Docker. Players start with 5,000 chips and work through 4 rounds of card guessing with increasing multipliers (2x, 3x, 4x, 20x). Player accounts and balances persist across sessions using a SQLite database.

## How to Play

Each round you guess something about a face-down card:
- **Round 1 (2x):** Red or Black?
- **Round 2 (3x):** Higher or Lower than the first card?
- **Round 3 (4x):** Inside or Outside the range of the first two cards?
- **Round 4 (20x):** Guess the exact suit.

Guess all 4 correctly and you ride the full bus at 20x your bet. One wrong guess and you lose your bet.

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)
- [GIT](https://git-scm.com/install/)

---

**1. Clone the repo**

```bash
git clone https://github.com/yourusername/ride-the-bus.git
cd ride-the-bus
```

**2. Start the container**

```bash
docker compose up --build -d
```

**3. Open the game**

Go to `http://localhost:5001` in your browser.

---

## Updating

If you pulled the image from Docker Hub and a new version is available:

```bash
docker compose pull
docker compose up -d
```

If you are running from source and made code changes:

```bash
docker compose restart
```

---

## Project Structure

```
ride-the-bus/
  server.py              - Flask app and API routes
  requirements.txt       - Python dependencies
  Dockerfile             - Container build instructions
  docker-compose.yml     - Container run configuration
  game_logic/
    deck.py              - Card deck building and shuffling
    account.py           - SQLite account management
    ride_the_bus.py      - Game logic (phases, guessing, payouts)
  templates/
    ride_the_bus.html    - Game UI (talks to server via fetch)
  static/
    css/style.css        - Retro pixel art styling
  data/                  - Created automatically, holds accounts.db
```

## Data Persistence

Player balances are stored in a SQLite database at `data/accounts.db`. This folder is mounted as a volume so data survives container restarts and updates. Make sure you do not delete the `data/` folder if you want to keep player balances.
