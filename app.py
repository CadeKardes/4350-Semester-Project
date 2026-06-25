from flask import Flask, render_template, request, jsonify
from game.logic import handle_guess
from game.logic import reset_game

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("game.html")


@app.route("/guess", methods=["POST"])
def guess():
    data = request.get_json()

    player_guess = data.get("guess")

    result = handle_guess(player_guess)

    return jsonify(result)


@app.route("/reset", methods=["POST"])
def reset():

    reset_game()

    return jsonify({
        "success": True
    })


if __name__ == "__main__":
    app.run(debug=True)