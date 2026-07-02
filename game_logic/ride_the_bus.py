from game_logic.deck import build_deck, is_red

MULTIPLIERS = [2, 3, 4, 20]

PHASE_QUESTIONS = [
    'Red or Black?  (2x)',
    'Higher or Lower?  (3x)',
    'Inside or Outside?  (4x)',
    'Guess the Suit!  (20x)',
]

def new_game(bet):
    """
    Start a new game. Returns the initial game state dict.
    bet: integer chip amount already deducted from the player's balance.
    """
    deck = build_deck()
    # Draw all 4 cards upfront and store them. The frontend only reveals them one phase at a time.
    drawn = [deck.pop() for _ in range(4)]
    return {
        'deck': deck,
        'drawn': drawn,
        'phase': 0,
        'bet': bet,
        'status': 'active',  # active | won | lost | cashed
        'payout': 0,
        'log': [],
    }

def evaluate_guess(state, guess):
    """
    Evaluate the player's guess for the current phase.
    Mutates state and returns it with updated status/log.
    Ties always count as correct.
    """
    phase = state['phase']
    card = state['drawn'][phase]
    drawn = state['drawn']

    correct = False

    if phase == 0:
        # Round 1: Red or Black?
        correct = guess == ('red' if is_red(card) else 'black')

    elif phase == 1:
        # Round 2: Higher or Lower? (ties count as correct)
        prev_val = drawn[0]['val']
        cur_val  = card['val']
        if guess == 'higher':
            correct = cur_val >= prev_val
        else:
            correct = cur_val <= prev_val

    elif phase == 2:
        # Round 3: Inside or Outside? (ties count as correct)
        vals = sorted([drawn[0]['val'], drawn[1]['val']])
        cur_val = card['val']
        if guess == 'inside':
            correct = vals[0] <= cur_val <= vals[1]
        else:
            correct = cur_val <= vals[0] or cur_val >= vals[1]

    elif phase == 3:
        # Round 4: Guess the exact suit
        correct = guess == card['suit']

    if correct:
        mult = MULTIPLIERS[phase]
        winnings = state['bet'] * mult
        state['log'].append({
            'type': 'win',
            'msg': f"Round {phase + 1}: Correct! ({mult}x) Potential: {winnings:,} chips"
        })
        state['phase'] += 1
        # If all 4 phases cleared, mark as won immediately
        if state['phase'] >= 4:
            state['status'] = 'won'
            state['payout'] = winnings
    else:
        state['log'].append({
            'type': 'lose',
            'msg': f"Round {phase + 1}: Wrong. Bet lost."
        })
        state['phase'] += 1
        state['status'] = 'lost'
        state['payout'] = 0

    return state

def cash_out(state):
    """
    Player cashes out after a correct guess.
    Pays out at the multiplier for the last completed phase.
    """
    completed_phase = state['phase'] - 1
    if completed_phase < 0:
        return state  # can't cash out before any correct guesses
    payout = state['bet'] * MULTIPLIERS[completed_phase]
    state['payout'] = payout
    state['status'] = 'cashed'
    state['log'].append({
        'type': 'cash',
        'msg': f"Cashed out: +{payout:,} chips"
    })
    return state

def get_phase_question(phase):
    """Return the question string for a given phase index."""
    if 0 <= phase < len(PHASE_QUESTIONS):
        return PHASE_QUESTIONS[phase]
    return ''

def get_multiplier(phase):
    """Return the multiplier for a given phase index."""
    if 0 <= phase < len(MULTIPLIERS):
        return MULTIPLIERS[phase]
    return 1

def visible_cards(state):
    """
    Return only the cards that have been revealed so far (up to current phase),
    serialized as plain dicts safe to send as JSON.
    The card for the current phase (not yet guessed) is sent face-down.
    """
    phase = state['phase']
    if state['status'] != 'active':
        # Game over - reveal all drawn cards up to the phase that ended things
        end = min(phase, 4)
        return [_serialize_card(state['drawn'][i], face_down=False) for i in range(end)]

    cards = []
    for i in range(phase + 1):
        face_down = (i == phase)  # current card is face down until guess is made
        cards.append(_serialize_card(state['drawn'][i], face_down=face_down))
    return cards

def _serialize_card(card, face_down=False):
    return {
        'rank': card['rank'],
        'suit': card['suit'],
        'val':  card['val'],
        'red':  is_red(card),
        'face_down': face_down,
    }
