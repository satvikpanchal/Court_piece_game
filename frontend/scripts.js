const startGameBtn = document.getElementById("startGameBtn");
const trumpPickerSection = document.getElementById("trumpPickerSection");
const trumpSelect = document.getElementById("trumpSelect");
const setTrumpBtn = document.getElementById("setTrumpBtn");

const trumpPickerSpan = document.getElementById("trumpPicker");
const trumpSuitSpan = document.getElementById("trumpSuit");
const currentTurnSpan = document.getElementById("currentTurn");
const currentRoundSpan = document.getElementById("currentRound");
const gameOverStatusSpan = document.getElementById("gameOverStatus");
const scoreBoardDiv = document.getElementById("scoreBoard");

const player1HandDiv = document.getElementById("player1Hand");
const player2HandDiv = document.getElementById("player2Hand");
const player3HandDiv = document.getElementById("player3Hand");
const player4HandDiv = document.getElementById("player4Hand");
const trickCenterDiv = document.getElementById("trickCenter");

// Start Game
startGameBtn.addEventListener("click", async () => {
  await fetch("/start_game", { method: "POST" });
  const data = await (await fetch("/get_game_state")).json();
  updateUI(data);
});

// Set Trump
setTrumpBtn.addEventListener("click", async () => {
  const suit = trumpSelect.value;
  if (!suit) return;
  await fetch("/pick_trump", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ suit })
  });
  const data = await (await fetch("/get_game_state")).json();
  updateUI(data);
});

async function playCard(playerName, cardIndex) {
  await fetch("/play_card", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player: playerName, cardIndex })
  });
  const data = await (await fetch("/get_game_state")).json();
  updateUI(data);
}

function updateUI(gameData) {
  const {
    players,
    trump_picker,
    trump_suit,
    current_turn,
    scores,
    current_round,
    game_over,
    current_trick
  } = gameData;

  trumpPickerSpan.textContent = trump_picker || "";
  trumpSuitSpan.textContent = trump_suit || "";
  currentTurnSpan.textContent = "Player " + (current_turn + 1);
  currentRoundSpan.textContent = current_round;
  gameOverStatusSpan.textContent = game_over ? "Yes" : "No";

  // Show/hide trump picking area
  if (trump_picker && !trump_suit) {
    trumpPickerSection.style.display = "inline-block";
  } else {
    trumpPickerSection.style.display = "none";
  }

  renderScores(scores);

  renderHand("Player 1", players["Player 1"], player1HandDiv, current_turn);
  renderHand("Player 2", players["Player 2"], player2HandDiv, current_turn);
  renderHand("Player 3", players["Player 3"], player3HandDiv, current_turn);
  renderHand("Player 4", players["Player 4"], player4HandDiv, current_turn);

  renderTrickCenter(current_trick);

  if (game_over) {
    alert("Game Over! Check scoreboard for final results.");
  }
}

function renderScores(scores) {
  scoreBoardDiv.innerHTML = "<h3>Scores</h3>";
  for (const p in scores) {
    const pElem = document.createElement("p");
    pElem.textContent = `${p}: ${scores[p]} tricks`;
    scoreBoardDiv.appendChild(pElem);
  }
}

function renderHand(playerName, cards, container, currentTurn) {
  container.innerHTML = "";
  if (!cards) return;

  const isPlayerTurn = (playerName === "Player " + (currentTurn + 1));

  cards.forEach((cardData, index) => {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("card");

    const img = document.createElement("img");
    img.src = cardData.image;
    img.alt = `${cardData.value} of ${cardData.suit}`;
    cardDiv.appendChild(img);

    // Double-click approach
    cardDiv.addEventListener("click", () => {
      if (!isPlayerTurn) return;
      if (cardDiv.classList.contains("selected")) {
        cardDiv.classList.remove("selected");
        playCard(playerName, index);
      } else {
        // Unselect other cards, select this one
        Array.from(container.children).forEach(c => c.classList.remove("selected"));
        cardDiv.classList.add("selected");
      }
    });

    container.appendChild(cardDiv);
  });
}

function renderTrickCenter(trick) {
  trickCenterDiv.innerHTML = "";
  if (!trick || trick.length === 0) {
    return;
  }
  trick.forEach(([player, card]) => {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("trick-card");
    const img = document.createElement("img");
    img.src = card.image;
    img.alt = `${card.value} of ${card.suit}`;
    cardDiv.appendChild(img);
    trickCenterDiv.appendChild(cardDiv);
  });
}
