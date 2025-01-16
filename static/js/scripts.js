let playerId = null;
let accessToken = null;

document.getElementById("register").addEventListener("click", () => {
    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;
    const confirmPassword = document.getElementById("reg-confirm-password").value;

    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, confirm_password: confirmPassword }),
    })
        .then(response => {
            if (!response.ok) throw new Error("Registration failed");
            return response.json();
        })
        .then(data => {
            alert(data.message);
        })
        .catch(err => alert(err.message));
});

document.getElementById("login").addEventListener("click", () => {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${username}&password=${password}`,
    })
        .then(response => {
            if (!response.ok) throw new Error("Invalid credentials");
            return response.json();
        })
        .then(data => {
            accessToken = data.access_token;
            playerId = username;
            alert(`Logged in as ${playerId}`);
            document.getElementById("login-container").style.display = "none";
            document.getElementById("register-container").style.display = "none";
            document.getElementById("game-actions").style.display = "block";
        })
        .catch(err => alert(err.message));
});

document.getElementById("start-game").addEventListener("click", () => {
    fetch("/create_game", {
        method: "GET",
        headers: { Authorization: `Bearer ${accessToken}` },
    })
        .then(response => response.json())
        .then(data => {
            alert("Game started with Game ID: " + data.game_id);
            document.getElementById("deal-cards").disabled = false;
            document.getElementById("game-id").innerText = data.game_id;
        })
        .catch(err => alert("Failed to start game"));
});

document.getElementById("join-game").addEventListener("click", () => {
    const gameId = prompt("Enter Game ID:");
    fetch(`/join_game/${gameId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
        body: JSON.stringify({ username: playerId }),
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            document.getElementById("deal-cards").disabled = false;
            document.getElementById("game-id").innerText = gameId;
        })
        .catch(err => alert("Failed to join game"));
});

document.getElementById("deal-cards").addEventListener("click", () => {
    const gameId = document.getElementById("game-id").innerText;
    fetch(`/deal_cards/${gameId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
    })
        .then(response => response.json())
        .then(data => {
            displayPlayerHand(data.hands[playerId]);
            alert("First 5 cards dealt! Select trump.");
        })
        .catch(err => alert("Failed to deal cards"));
});

document.getElementById("select-trump").addEventListener("click", () => {
    const gameId = document.getElementById("game-id").innerText;
    const trump = prompt("Select trump suit (hearts, diamonds, clubs, spades):");
    fetch(`/select_trump/${gameId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
        body: JSON.stringify({ player_id: playerId, trump: trump }),
    })
        .then(response => response.json())
        .then(data => {
            displayPlayerHand(data.hands[playerId]);
            alert(`Trump selected: ${trump}. Remaining cards dealt.`);
        })
        .catch(err => alert("Failed to select trump"));
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
    const gameId = document.getElementById("game-id").innerText;
    fetch(`/play_card?game_id=${gameId}&player_id=${playerId}&card_code=${cardCode}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
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

function showToast(message, duration = 5000) {
    const toast = document.createElement("div");
    toast.innerText = message;
    toast.className = "toast";
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}