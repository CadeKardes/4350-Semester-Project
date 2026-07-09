let audioStarted = false;
let audioMuted = false;
let awaitingContinue = false;
let pendingRound = 1;
let lastCorrectImage = "";
let animationPlaying = false;

function updateButtons(round) {

    const container = document.getElementById("buttonContainer");

    if (round === 1) {
        container.innerHTML = `
            <button onclick="makeGuess('Red')">Red</button>
            <button onclick="makeGuess('Black')">Black</button>
        `;
    }

    else if (round === 2) {
        container.innerHTML = `
            <button onclick="makeGuess('Higher')">Higher</button>
            <button onclick="makeGuess('Lower')">Lower</button>
        `;
    }

    else if (round === 3) {
        container.innerHTML = `
            <button onclick="makeGuess('Inside')">Inside</button>
            <button onclick="makeGuess('Outside')">Outside</button>
        `;
    }

    else if (round === 4) {
        container.innerHTML = `
            <button onclick="makeGuess('Hearts')">Hearts</button>
            <button onclick="makeGuess('Diamonds')">Diamonds</button>
            <button onclick="makeGuess('Clubs')">Clubs</button>
            <button onclick="makeGuess('Spades')">Spades</button>
        `;
    }
}

function flipCard(imagePath) {

    const inner =
        document.getElementById("cardInner");

    const front =
        document.getElementById("cardFront");

    // Put revealed card on front face
    front.src = imagePath;

    // Flip the whole card
    inner.style.transform =
        "rotateY(180deg)";
}

async function makeGuess(guess) {
    // Prevent input during animations
    if (animationPlaying) {
        return;
    }

    if (!audioStarted) {

        // Pirate music
        const music =
            document.getElementById("ambienceAudio");

        music.volume = 0.25;

        music.play();


        // Tavern crowd ambience
        const tavern =
            document.getElementById("tavernAudio");

        tavern.volume = 0.15;

        tavern.play();

        audioStarted = true;
    }

    const response = await fetch("/guess", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            guess: guess
        })
    });

    const data = await response.json();

    // STOP if backend says game over
    if (data.game_over && !data.card) {

        return;
    }

    // Lock input during animation
    animationPlaying = true;

    // Hide gameplay buttons
    document.getElementById("buttonContainer")
        .style.display = "none";

    // Show current card
    const imagePath =
        `/static/images/cards/${data.image}`;

    flipCard(imagePath);

    // Correct guess
    if (data.correct) {

        document.getElementById("resultText").innerText =
            "Correct!";

        // Hide guessing buttons temporarily
        document.getElementById("buttonContainer")
            .style.display = "none";

        // Show continue/cash out
        document.getElementById("continueContainer")
            .style.display = "flex";

        awaitingContinue = true;

        pendingRound = data.round;

        lastCorrectImage = data.image;
    }

    // Wrong guess
    else {

        document.getElementById("resultText").innerText =
            "Wrong!";

        // Remove gameplay buttons
        document.getElementById("buttonContainer").innerHTML = "";

        // Wait for flip animation before showing reset
        setTimeout(() => {

            document.getElementById("resetButton")
                .style.display = "block";

            // Unlock input
            animationPlaying = false;

        }, 800);
    }

    // Update info text
    document.getElementById("cardText").innerText =
        `Card: ${data.card}`;


    document.getElementById("roundText").innerText =
        `Round: ${data.round}`;

    // Win condition
    
}

function continueRound() {

    if (!awaitingContinue) {
        return;
    }

    const slotNumber = pendingRound - 1;

    const slot =
        document.getElementById(`slot${slotNumber}`);

    const cardContainer =
        document.getElementById("cardContainer");

    // Get positions
    const cardRect =
        cardContainer.getBoundingClientRect();

    const slotRect =
        slot.getBoundingClientRect();

    // Calculate movement distance
    const moveX =
        (slotRect.left + slotRect.width / 2)
        -
        (cardRect.left + cardRect.width / 2);

    const moveY =
        (slotRect.top + slotRect.height / 2)
        -
        (cardRect.top + cardRect.height / 2);

    // Animate card moving to slot
    cardContainer.classList.add("slideToSlot");

    cardContainer.style.transform =
        `translate(${moveX}px, ${moveY}px)
         scale(0.68)`;

    setTimeout(() => {

        // Put card into slot
        setTimeout(() => {

            slot.src =
                `/static/images/cards/${lastCorrectImage}`;

        }, 50);

        // FINAL ROUND WIN
        if (pendingRound > 4) {

            document.getElementById("resultText").innerText =
                "YOU WON THE ROUND!";

            // Remove gameplay buttons
            document.getElementById("buttonContainer")
                .innerHTML = "";

            // Show continue container
            document.getElementById("continueContainer")
                .style.display = "flex";

            // Hide Continue button
            document.querySelector(
                "#continueContainer button:first-child"
            ).style.display = "none";

            // Rename Cash Out button
            document.querySelector(
                "#continueContainer button:last-child"
            ).innerText = "Play Again";
        }

        // Only reset moving card if game continues
        if (pendingRound <= 4) {

            cardContainer.classList.remove("slideToSlot");

            cardContainer.style.transform =
                "translate(0, 0) scale(1)";
        }

        // Final round won
        else {

            // Hide center card completely
            cardContainer.style.opacity = "0";
        }

        // Reset flip
        const cardInner =
            document.getElementById("cardInner");

        // Disable flip animation temporarily
        cardInner.style.transition = "none";

        cardInner.style.transform =
            "rotateY(0deg)";

        // Force browser reflow
        void cardInner.offsetWidth;

        // Re-enable flip animation
        cardInner.style.transition =
            "transform 0.8s ease";

        // Restore facedown card
        document.getElementById("cardFront").src =
            "/static/images/cards/back.png";

        // Only animate a new card if game is not won
        if (pendingRound <= 4) {

            // Animate new card entering
            cardContainer.classList.add("newCardEntrance");

            setTimeout(() => {

                cardContainer.classList.remove("newCardEntrance");

            }, 600);
        }

    }, 800);

    // Only continue normal gameplay if not won
    if (pendingRound <= 4) {

        // Hide continue buttons
        document.getElementById("continueContainer")
            .style.display = "none";

        // Wait until animations finish
        setTimeout(() => {

            updateButtons(pendingRound);

            document.getElementById("buttonContainer")
                .style.display = "block";

            // Unlock input
            animationPlaying = false;

        }, 600);
    }

    // Unlock immediately if final round won
    if (pendingRound > 4) {

        animationPlaying = false;
    }

    awaitingContinue = false;
}

async function cashOut() {

    // Restore continue button visibility
    document.querySelector(
        "#continueContainer button:first-child"
    ).style.display = "inline-block";

    // Restore cash out text
    document.querySelector(
        "#continueContainer button:last-child"
    ).innerText = "Cash Out";

    // Hide continue container
    document.getElementById("continueContainer")
        .style.display = "none";

    // Restart game
    await resetGame();
}

async function resetGame() {

    const cardContainer =
        document.getElementById("cardContainer");

    const cardInner =
        document.getElementById("cardInner");

    const cardFront =
        document.getElementById("cardFront");

    const wonGame =
        cardContainer.style.opacity === "0";
    
    // Animate filled slot cards downward
    for (let i = 1; i <= 4; i++) {

        const slot =
            document.getElementById(`slot${i}`);

        // Only animate real cards
        if (!slot.src.includes("empty.png")) {

            // Create temporary overlay copy
            const discardCard =
                slot.cloneNode(true);

            // Position it exactly over slot
            const rect =
                slot.getBoundingClientRect();

            discardCard.style.position = "fixed";

            discardCard.style.left =
                `${rect.left}px`;

            discardCard.style.top =
                `${rect.top}px`;

            discardCard.style.width =
                `${rect.width}px`;

            discardCard.style.height =
                `${rect.height}px`;

            discardCard.style.zIndex = "9999";

            discardCard.classList.add("slotDiscard");
            // Remove duplicate ID
            discardCard.removeAttribute("id");

            document.body.appendChild(discardCard);

            // Reset original slot instantly
            slot.src =
                "/static/images/cards/empty.png";
            
            // Force clean rendering
            slot.removeAttribute("style");

            // Remove animated clone afterward
            setTimeout(() => {

                if (discardCard.parentNode) {

                    discardCard.remove();
                }

            }, 700);
        }
    }

    // Only discard visible cards
    if (!wonGame) {

        cardContainer.classList.add("resetDiscard");
    }

    // Wait for discard animation
    setTimeout(async () => {

        await fetch("/reset", {
            method: "POST"
        });

        // Remove discard animation
        cardContainer.classList.remove("resetDiscard");

        // Instantly reset flip state
        cardInner.style.transition = "none";

        cardInner.style.transform =
            "rotateY(0deg)";

        void cardInner.offsetWidth;

        cardInner.style.transition =
            "transform 0.8s ease";

        // Restore facedown card
        cardFront.src =
            "/static/images/cards/back.png";

        // Disable transition first
        cardContainer.style.transition =
            "none";

        // Start below screen
        cardContainer.style.transform =
            "translateY(500px)";

        cardContainer.style.opacity =
            "0";

        // Force browser to register offscreen state
        void cardContainer.offsetWidth;

        // Re-enable animation
        cardContainer.style.transition =
            "transform 0.6s ease, opacity 0.6s ease";

        // Animate upward
        cardContainer.style.transform =
            "translateY(0)";

        cardContainer.style.opacity =
            "1";

    }, wonGame ? 0 : 700);

    document
        .getElementById("roundText")
        .innerText =
        "Round: 1";

    document
        .getElementById("resultText")
        .innerText = "";

    document
        .getElementById("cardText")
        .innerText =
        "No card drawn yet.";

    document
        .getElementById("resetButton")
        .style.display = "none";

    setTimeout(() => {

        for (let i = 1; i <= 4; i++) {

            const slot =
                document.getElementById(`slot${i}`);

            // Remove animation class
            slot.classList.remove("slotDiscard");

            // Reset visual state
            slot.style.transform = "";
            slot.style.opacity = "";

            // Restore placeholder image
            slot.src =
                "/static/images/cards/empty.png";
        }

    }, wonGame ? 0 : 700);

    document.getElementById("buttonContainer").innerHTML = "";

    document.getElementById("continueContainer")
        .style.display = "none";

    setTimeout(() => {

        updateButtons(1);

        document.getElementById("buttonContainer")
            .style.display = "block";

        // Unlock input
        animationPlaying = false;

    }, 600);
}

function goFullscreen() {

    const button =
        document.getElementById("fullscreenButton");

    // ENTER fullscreen
    if (!document.fullscreenElement) {

        document.documentElement.requestFullscreen();

        button.innerText =
            "Exit Fullscreen";
    }

    // EXIT fullscreen
    else {

        document.exitFullscreen();

        button.innerText =
            "Enter Fullscreen";
    }
}

document.addEventListener("fullscreenchange", () => {

    const button =
        document.getElementById("fullscreenButton");

    if (document.fullscreenElement) {

        button.innerText =
            "Exit Fullscreen";
    }

    else {

        button.innerText =
            "Enter Fullscreen";
    }
});

function toggleAudio() {

    const music =
        document.getElementById("ambienceAudio");

    const tavern =
        document.getElementById("tavernAudio");

    audioMuted = !audioMuted;

    music.muted = audioMuted;

    tavern.muted = audioMuted;

    document.getElementById("soundButton").innerText =
        audioMuted ? "🔇" : "🔊";
}

updateButtons(1); 