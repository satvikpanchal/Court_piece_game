from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, validator
from typing import List, Dict
import bcrypt
import sqlite3
import uvicorn

# FastAPI app
app = FastAPI()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Database setup
DATABASE = "court_piece.db"
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

# User models
class User(BaseModel):
    username: str
    password: str
    confirm_password: str

    @validator("confirm_password")
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

# WebSocket for real-time communication
@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    await websocket.send_text(f"Connected to game {game_id}")
    while True:
        try:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
        except Exception as e:
            print(f"WebSocket error: {e}")
            break

# Game setup and card API integration
@app.get("/create_game")
async def create_game():
    import requests
    response = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    if response.status_code == 200:
        deck_data = response.json()
        return {"game_id": deck_data["deck_id"]}
    else:
        raise HTTPException(status_code=500, detail="Error creating game")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
