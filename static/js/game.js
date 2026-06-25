function updateButtons(round) {
    const container = document.getElementById("buttonContainer");

    if (round === 1) {
        container.innerHTML = `
            <button onclick="makeGuess('Red')">Red</button>
            <button onclick="makeGuess('Black')">Black</button>
        `;
    } else if (round === 2) {
        container.innerHTML = `
            <button onclick="makeGuess('Higher')">Higher</button>
            <button onclick="makeGuess('Lower')">Lower</button>
        `;
    } else if (round === 3) {
        container.innerHTML = `
            <button onclick="makeGuess('Inside')">Inside</button>
            <button onclick="makeGuess('Outside')">Outside</button>
        `;
    } else if (round === 4) {
        container.innerHTML = `
            <button onclick="makeGuess('Hearts')">Hearts</button>
            <button onclick="makeGuess('Diamonds')">Diamonds</button>
            <button onclick="makeGuess('Clubs')">Clubs</button>
            <button onclick="makeGuess('Spades')">Spades</button>
        `;
    } else {
        container.innerHTML = "";
    }
}

async function makeGuess(guess) {
    const response = await fetch("/guess", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ guess: guess })
    });

    const data = await response.json();

    document.getElementById("cardText").innerText =
        `Card Drawn: ${data.card}`;

    if (data.correct) {
        document.getElementById("resultText").innerText = "Correct!";
    } else {
        document.getElementById("resultText").innerText = "Wrong! Game over.";
        document.getElementById("buttonContainer").innerHTML = "";
        return;
    }

    if (data.won) {
        document.getElementById("resultText").innerText = "You won!";
        document.getElementById("buttonContainer").innerHTML = "";
        return;
    }

    document.getElementById("roundText").innerText =
        `Round: ${data.round}`;

    updateButtons(data.round);
}

async function resetGame() {
    await fetch("/reset", {
        method: "POST"
    });

    document.getElementById("roundText").innerText = "Round: 1";
    document.getElementById("cardText").innerText = "No card drawn yet.";
    document.getElementById("resultText").innerText = "";

    updateButtons(1);
}

updateButtons(1);