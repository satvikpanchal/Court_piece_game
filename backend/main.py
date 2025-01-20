from fastapi import FastAPI
from game_logic import TrumpGame
from fastapi.staticfiles import StaticFiles

app = FastAPI()
game = TrumpGame()

# Mount frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Trump Card Game!"}

@app.post("/start")
def start_game():
    game.fetch_new_deck()
    game.distribute_cards()
    trump_picker = game.select_trump_picker()
    return {"message": "Game started", "trump_picker": trump_picker}

@app.post("/set-trump")
def set_trump(suit: str):
    return {"message": game.set_trump_suit(suit)}

@app.get("/get-players")
def get_players():
    return game.get_players()

@app.post("/play-card/{player_id}/{card_index}")
def play_card(player_id: int, card_index: int):
    lead_suit = game.trump_suit if game.current_turn == 0 else None
    return game.play_turn(player_id, card_index, lead_suit)
