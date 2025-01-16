from fastapi import FastAPI, WebSocket, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator
from typing import List, Dict
import bcrypt
import sqlite3
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE = os.getenv("DATABASE_PATH", "court_piece.db")

# FastAPI app
app = FastAPI()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# In-memory storage for game states
game_states = {}

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
init_db()

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

# Root route
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

# Game endpoints
@app.get("/create_game")
async def create_game():
    import uuid
    game_id = str(uuid.uuid4())[:8]
    game_states[game_id] = {"players": [], "hands": {}}
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
    response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error creating deck")

    deck_id = response.json()["deck_id"]
    draw_response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=52")
    if draw_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error dealing cards")

    cards = draw_response.json()["cards"]
    hands = [cards[i:i + 13] for i in range(0, 52, 13)]
    game["hands"] = dict(zip(game["players"], hands))
    return {"message": "Cards dealt successfully", "hands": game["hands"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)