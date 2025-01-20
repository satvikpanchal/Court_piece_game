import requests
import random

class TrumpGame:
    def __init__(self):
        self.deck_id = None
        self.players = {f"Player {i+1}": [] for i in range(4)}
        self.trump_picker = None
        self.trump_suit = None
        self.current_turn = 0
        self.scores = {f"Player {i+1}": 0 for i in range(4)}

    def fetch_new_deck(self):
        response = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
        if response.status_code == 200:
            self.deck_id = response.json()['deck_id']
        else:
            print("Error fetching deck from API.")

    def draw_cards(self, count):
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={count}")
        if response.status_code == 200:
            return response.json()['cards']
        else:
            return []

    def distribute_cards(self):
        initial_count = 5
        remaining_count = 47
        for player in self.players:
            self.players[player] = self.draw_cards(initial_count)

        if remaining_count > 0:
            remaining_cards = self.draw_cards(remaining_count)
            player_index = 0
            for card in remaining_cards:
                current_player = f"Player {player_index + 1}"
                self.players[current_player].append(card)
                player_index = (player_index + 1) % 4

    def select_trump_picker(self):
        self.trump_picker = random.choice(list(self.players.keys()))
        return self.trump_picker

    def set_trump_suit(self, suit):
        if suit in ['HEARTS', 'DIAMONDS', 'CLUBS', 'SPADES']:
            self.trump_suit = suit
            return f"Trump suit set to {self.trump_suit}."
        return "Invalid suit choice."

    def play_turn(self, player_id, card_index, lead_suit=None):
        player = f"Player {player_id}"
        if player not in self.players or not (0 <= card_index < len(self.players[player])):
            return {"error": "Invalid move"}

        selected_card = self.players[player][card_index]

        # Enforce lead suit rule
        if lead_suit and selected_card['suit'] != lead_suit:
            if any(card['suit'] == lead_suit for card in self.players[player]):
                return {"error": f"You must play a card of the lead suit ({lead_suit})"}

        self.players[player].pop(card_index)
        self.current_turn = (self.current_turn + 1) % 4
        return {"player": player, "card": selected_card}

    def get_players(self):
        return self.players

    def get_trump_suit(self):
        return self.trump_suit
