import requests

BASE_URL = "http://127.0.0.1:8000"

users = [
]

# Register users
for user in users:
    response = requests.post(f"{BASE_URL}/register", json={
        "username": user["username"],
        "password": user["password"],
        "confirm_password": user["password"]
    })
    print(response.json())

# Login users and get tokens
tokens = {}
for user in users:
    response = requests.post(f"{BASE_URL}/token", data={
        "username": user["username"],
        "password": user["password"]
    })
    tokens[user["username"]] = response.json()["access_token"]

# Create a game
response = requests.get(f"{BASE_URL}/create_game", headers={
    "Authorization": f"Bearer {tokens['player1']}"
})
game_id = response.json()["game_id"]
print(f"Game ID: {game_id}")

# Join the game with all players
for user in users:
    response = requests.post(f"{BASE_URL}/join_game/{game_id}", json={
        "username": user["username"]
    }, headers={
        "Authorization": f"Bearer {tokens[user['username']]}"
    })
    print(response.json())

# Deal cards
response = requests.post(f"{BASE_URL}/deal_cards/{game_id}", headers={
    "Authorization": f"Bearer {tokens['player1']}"
})
print(response.json())

# Select trump
response = requests.post(f"{BASE_URL}/select_trump/{game_id}", json={
    "player_id": "player1",
    "trump": "hearts"
}, headers={
    "Authorization": f"Bearer {tokens['player1']}"
})
print(response.json())

# Play a card (example)
response = requests.post(f"{BASE_URL}/play_card", params={
    "game_id": game_id,
    "player_id": "player1",
    "card_code": "AS"  # Example card code
}, headers={
    "Authorization": f"Bearer {tokens['player1']}"
})
print(response.json())