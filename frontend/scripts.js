document.getElementById("start-btn").addEventListener("click", () => {
    fetch("/start", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            alert(`${data.message} - ${data.trump_picker} will pick trump.`);
            loadPlayers();
        })
        .catch(error => console.error("Error:", error));
});

function loadPlayers() {
    fetch("/get-players")
        .then(response => response.json())
        .then(players => {
            let playerContainer = document.getElementById("players");
            playerContainer.innerHTML = "";
            for (let player in players) {
                let div = document.createElement("div");
                div.className = "player-cards";
                div.innerHTML = `<h3>${player}</h3>`;
                
                players[player].forEach((card, index) => {
                    let cardBtn = document.createElement("button");
                    cardBtn.textContent = `${card.value} of ${card.suit}`;
                    cardBtn.onclick = () => playCard(player.split(" ")[1], index);
                    div.appendChild(cardBtn);
                });

                playerContainer.appendChild(div);
            }
        });
}

function playCard(playerId, cardIndex) {
    fetch(`/play-card/${playerId}/${cardIndex}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(`${data.player} played ${data.card.value} of ${data.card.suit}`);
                loadPlayers();
            }
        })
        .catch(error => console.error("Error:", error));
}
