from fastapi import FastAPI, WebSocket, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from typing import List, Dict
import bcrypt
import sqlite3
import uvicorn
import os
import uuid

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv()
DATABASE = os.getenv("DATABASE_PATH", "court_piece.db")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates for HTML files
templates = Jinja2Templates(directory="templates")

# Root route for serving the index.html
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# User model
class User(BaseModel):
    username: str
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        if "password" in values and confirm_password != values["password"]:
            raise ValueError("Passwords do not match")
        return confirm_password

# Utility functions
def get_user(username: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username: str, password: str):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Court Piece API is running!"}

# Auth endpoints
@app.post("/register")
async def register(user: User):
    create_user(user.username, user.password)
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user[2]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": user[1], "token_type": "bearer"}

# Game states stored in memory for simplicity
game_states = {}

@app.get("/create_game")
async def create_game():
    game_id = str(uuid.uuid4())[:8]
    game_states[game_id] = {"players": [], "hands": {}, "trump": None, "turn": None, "pairs": {1: 0, 2: 0}, "table": []}
    return {"game_id": game_id}

@app.post("/join_game/{game_id}")
async def join_game(game_id: str, username: str):
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")

    game = game_states[game_id]
    if username in game["players"]:
        return {"message": f"{username} already joined the game."}
    elif len(game["players"]) >= 4:
        raise HTTPException(status_code=400, detail="Game is already full")

    game["players"].append(username)
    return {"message": f"{username} joined game {game_id}"}

@app.post("/deal_cards/{game_id}")
async def deal_cards(game_id: str):
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")

    game = game_states[game_id]
    if len(game["players"]) < 4:
        raise HTTPException(status_code=400, detail="Not enough players to start the game")

    import requests
    response = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error creating deck")

    deck_id = response.json()["deck_id"]
    draw_response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=52")
    if draw_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error dealing cards")

    cards = draw_response.json()["cards"]
    hands = [cards[i:i + 13] for i in range(0, 52, 13)]
    game["hands"] = dict(zip(game["players"], hands))

    # Deal first 5 cards to each player
    first_five_cards = {player: hand[:5] for player, hand in game["hands"].items()}
    return {"message": "First 5 cards dealt", "hands": first_five_cards}

@app.post("/select_trump/{game_id}")
async def select_trump(game_id: str, player_id: str, trump: str):
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")

    game = game_states[game_id]
    if player_id not in game["players"]:
        raise HTTPException(status_code=400, detail="Player not in game")

    game["trump"] = trump

    # Deal remaining cards
    remaining_cards = {player: hand[5:] for player, hand in game["hands"].items()}
    for player, cards in remaining_cards.items():
        game["hands"][player] = game["hands"][player][:5] + cards

    return {"message": f"Trump selected: {trump}", "hands": game["hands"]}

@app.post("/play_card")
async def play_card(game_id: str, player_id: str, card_code: str):
    if game_id not in game_states:
        raise HTTPException(status_code=404, detail="Game not found")

    game = game_states[game_id]
    if player_id not in game["players"]:
        raise HTTPException(status_code=400, detail="Player not in game")

    # Implement game logic here
    # Update game state, check for pairs, update turn, etc.
    game["table"].append({"player": player_id, "card": card_code})

    return {"message": "Card played", "table": game["table"], "tricks": game["pairs"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)