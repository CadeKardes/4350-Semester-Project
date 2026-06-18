from game.game_state import GameState

game_state = GameState()


def reset_game():
    game_state.reset()


def handle_guess(player_guess):

    # Stop gameplay if failed
    if hasattr(game_state, "game_over") and game_state.game_over:
        return {
            "game_over": True
        }

    card = game_state.deck.draw_card()

    if card is None:
        return {
            "error": "Deck empty."
        }

    correct = False

    # ROUND 1 — RED OR BLACK
    if game_state.round == 1:

        correct = (
            player_guess.lower()
            == card["color"].lower()
        )

    # ROUND 2 — HIGHER OR LOWER
    elif game_state.round == 2:

        previous = game_state.cards[0]

        if player_guess.lower() == "higher":
            correct = card["value"] > previous["value"]

        elif player_guess.lower() == "lower":
            correct = card["value"] < previous["value"]

    # ROUND 3 — INSIDE OR OUTSIDE
    elif game_state.round == 3:

        first = game_state.cards[0]
        second = game_state.cards[1]

        low = min(first["value"], second["value"])
        high = max(first["value"], second["value"])

        inside = (
            low < card["value"] < high
        )

        if player_guess.lower() == "inside":
            correct = inside

        elif player_guess.lower() == "outside":
            correct = not inside

    # ROUND 4 — SUIT
    elif game_state.round == 4:

        correct = (
            player_guess.lower()
            == card["suit"].lower()
        )

    # CORRECT GUESS
    if correct:

        game_state.cards.append(card)

        game_state.round += 1

    # WRONG GUESS
    else:

        game_state.game_over = True

    won = game_state.round > 4

    current_round = game_state.round

    return {
        "card": f'{card["name"]} of {card["suit"]}',

        "image":
            f'{card["name"].lower()}_of_{card["suit"].lower()}.png',

        "correct": correct,

        "tankards": game_state.tankards,

        "round": current_round,

        "won": won,

        "game_over":
            getattr(game_state, "game_over", False)
    }