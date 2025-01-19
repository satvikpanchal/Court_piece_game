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
            print("Error drawing cards from API.")
            return []

    def distribute_cards(self, initial_count, remaining_count):
        print("Distributing cards to players...")
        for player in self.players:
            self.players[player] = self.draw_cards(initial_count)

        if remaining_count > 0:
            remaining_cards = self.draw_cards(remaining_count)
            player_index = 0
            for card in remaining_cards:
                current_player = f"Player {player_index + 1}"
                self.players[current_player].append(card)
                player_index = (player_index + 1) % 4

    def show_initial_cards(self, player):
        print(f"{player}'s initial cards:")
        for idx, card in enumerate(self.players[player][:5]):
            print(f"{idx+1}: {card['value']} of {card['suit']}")

    def select_trump_picker(self):
        self.trump_picker = random.choice(list(self.players.keys()))
        print(f"{self.trump_picker} has been selected to choose the trump suit.")

    def pick_trump_suit(self):
        self.show_initial_cards(self.trump_picker)
        suits = ['HEARTS', 'DIAMONDS', 'CLUBS', 'SPADES']
        while True:
            chosen_suit = input(f"{self.trump_picker}, choose the trump suit ({', '.join(suits)}): ").upper()
            if chosen_suit in suits:
                self.trump_suit = chosen_suit
                print(f"Trump suit is {self.trump_suit}.")
                break
            else:
                print("Invalid choice. Please choose again.")

    def play_turn(self, lead_suit):
        current_player = f"Player {self.current_turn + 1}"
        print(f"{current_player}'s turn.")
        self.show_player_cards(current_player)

        while True:
            try:
                card_index = int(input(f"{current_player}, pick a card to play (1-{len(self.players[current_player])}): ")) - 1
                if 0 <= card_index < len(self.players[current_player]):
                    selected_card = self.players[current_player][card_index]
                    # Enforce rule: If a player has a card of the lead suit, they must play it
                    if lead_suit and selected_card['suit'] != lead_suit:
                        if any(card['suit'] == lead_suit for card in self.players[current_player]):
                            print(f"You must play a card of the lead suit ({lead_suit}). Try again.")
                            continue
                    self.players[current_player].pop(card_index)
                    self.current_turn = (self.current_turn + 1) % 4
                    return current_player, selected_card
                else:
                    print("Invalid card number. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def show_player_cards(self, player):
        print(f"{player}'s cards:")
        for idx, card in enumerate(self.players[player]):
            print(f"{idx+1}: {card['value']} of {card['suit']}")

    def determine_winner(self, trick):
        lead_suit = trick[0][1]['suit']
        highest_card = None
        winner = None

        for player, card in trick:
            if card['suit'] == self.trump_suit:
                if highest_card is None or card['suit'] == self.trump_suit and self.card_value(card['value']) > self.card_value(highest_card['value']):
                    highest_card = card
                    winner = player
            elif card['suit'] == lead_suit:
                if highest_card is None or card['suit'] == lead_suit and self.card_value(card['value']) > self.card_value(highest_card['value']):
                    highest_card = card
                    winner = player

        print(f"{winner} wins the trick with {highest_card['value']} of {highest_card['suit']}.")
        self.scores[winner] += 1

    def card_value(self, value):
        values = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
            "JACK": 11, "QUEEN": 12, "KING": 13, "ACE": 14
        }
        return values[value]

    def play_game(self):
        for round_number in range(13):
            print(f"\nRound {round_number + 1}! Current Scores: {self.scores}")
            trick = []
            lead_suit = None

            for turn in range(4):
                player, card = self.play_turn(lead_suit)
                trick.append((player, card))
                if lead_suit is None:
                    lead_suit = card['suit']

            self.determine_winner(trick)

        game_winner = max(self.scores, key=self.scores.get)
        print(f"\nGame Over! {game_winner} wins with {self.scores[game_winner]} tricks.")

    def start_game(self):
        print("Starting the game...")
        self.fetch_new_deck()
        self.distribute_cards(5, 47)
        self.select_trump_picker()
        self.pick_trump_suit()
        print("All cards have been distributed. Let the game begin!")
        self.play_game()

if __name__ == "__main__":
    TrumpGame().start_game()
