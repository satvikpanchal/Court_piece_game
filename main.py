from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from game_logic import TrumpGame

app = FastAPI()

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Single in-memory instance of the game
game = TrumpGame()

class PickTrumpModel(BaseModel):
    suit: str

class PlayCardModel(BaseModel):
    player: str
    cardIndex: int

@app.get("/")
def serve_index():
    """Serve index.html"""
    return FileResponse("frontend/index.html")

@app.post("/start_game")
def start_game():
    game.start_game()
    return JSONResponse(get_game_data())

@app.post("/pick_trump")
def pick_trump(data: PickTrumpModel):
    if data.suit:
        game.pick_trump_suit(data.suit)
    return JSONResponse(get_game_data())

@app.post("/play_card")
def play_card(data: PlayCardModel):
    game.play_card(data.player, data.cardIndex)
    return JSONResponse(get_game_data())

@app.get("/get_game_state")
def get_game_state():
    return JSONResponse(get_game_data())

def get_game_data():
    return {
        "players": game.players,
        "trump_picker": game.trump_picker,
        "trump_suit": game.trump_suit,
        "current_turn": game.current_turn,
        "scores": game.scores,
        "current_round": game.current_round,
        "game_over": game.game_over,
        "current_trick": game.current_trick,
    }
