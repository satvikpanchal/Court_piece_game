let playerId = null;

document.getElementById("login").addEventListener("click", () => {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    })
        .then(response => response.json())
        .then(data => {
            playerId = data.player_id;
            alert(`Logged in as Player ${playerId}`);
            document.getElementById("login-container").style.display = "none";
            document.getElementById("game-actions").style.display = "block";
        })
        .catch(err => alert("Invalid credentials!"));
});

document.getElementById("start-game").addEventListener("click", () => {
    fetch("/new-game")
        .then(response => response.json())
        .then(data => {
            alert("Game started!");
            document.getElementById("deal-cards").disabled = false;
        });
});

document.getElementById("deal-cards").addEventListener("click", () => {
    fetch("/deal-cards")
        .then(response => response.json())
        .then(data => {
            displayPlayerHand(data.players[playerId]);
            alert("Cards dealt! Your turn.");
        });
});

function displayPlayerHand(cards) {
    const hand = document.getElementById("player-hand");
    hand.innerHTML = ""; // Clear previous cards
    cards.forEach(card => {
        const img = document.createElement("img");
        img.src = card.image;
        img.alt = card.code;
        img.addEventListener("click", () => playCard(card.code));
        hand.appendChild(img);
    });
}

function playCard(cardCode) {
    fetch(`/play-card?player_id=${playerId}&card_code=${cardCode}`, {
        method: "POST",
    })
        .then(response => response.json())
        .then(data => {
            alert("Card played!");
            updateGameTable(data.table);
            if (data.table.length === 0) {
                updateScores(data.tricks);
            }
        })
        .catch(err => console.error("Error playing card:", err));
}

function updateGameTable(table) {
    const tableDiv = document.getElementById("played-cards");
    tableDiv.innerHTML = ""; // Clear previous cards
    table.forEach(entry => {
        const img = document.createElement("img");
        img.src = entry.card.image;
        img.alt = entry.card.code;
        tableDiv.appendChild(img);
    });
}

function updateScores(tricks) {
    document.getElementById("team1-score").innerText = tricks[1];
    document.getElementById("team2-score").innerText = tricks[2];
}
