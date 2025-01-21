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
        self.current_round = 0
        self.current_trick = []
        self.lead_suit = None
        self.game_over = False

    def start_game(self):
        """Reinitialize the game state and deal new cards."""
        self.__init__()
        self.fetch_new_deck()
        self.distribute_cards(5, 47)
        self.select_trump_picker()

    def fetch_new_deck(self):
        resp = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
        if resp.status_code == 200:
            self.deck_id = resp.json()['deck_id']
        else:
            print("Error fetching deck from API.")

    def draw_cards(self, count):
        resp = requests.get(f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={count}")
        if resp.status_code == 200:
            return resp.json()['cards']
        else:
            print("Error drawing cards from API.")
            return []

    def distribute_cards(self, initial_count, remaining_count):
        for player in self.players:
            self.players[player] = self.draw_cards(initial_count)
        if remaining_count > 0:
            leftover = self.draw_cards(remaining_count)
            idx = 0
            for card in leftover:
                current_player = f"Player {idx + 1}"
                self.players[current_player].append(card)
                idx = (idx + 1) % 4

    def select_trump_picker(self):
        """Pick a random player to choose trump."""
        self.trump_picker = random.choice(list(self.players.keys()))

    def pick_trump_suit(self, suit):
        self.trump_suit = suit

    def play_card(self, player_name, card_index):
        """Handle playing a card, follow suit, track tricks, etc."""
        if self.game_over:
            return

        expected_player = f"Player {self.current_turn + 1}"
        if player_name != expected_player:
            return  # Not that player's turn

        player_hand = self.players[player_name]
        if card_index < 0 or card_index >= len(player_hand):
            return  # Invalid card index

        selected_card = player_hand[card_index]

        # Enforce follow-suit if lead suit is set
        if self.lead_suit is not None:
            has_lead_suit = any(c['suit'] == self.lead_suit for c in player_hand)
            if has_lead_suit and selected_card['suit'] != self.lead_suit:
                return  # Must follow suit

        # If first card in this trick, set the lead suit
        if len(self.current_trick) == 0:
            self.lead_suit = selected_card['suit']

        # Remove from hand, add to current trick
        player_hand.pop(card_index)
        self.current_trick.append((player_name, selected_card))

        # Advance turn
        self.current_turn = (self.current_turn + 1) % 4

        # If 4 cards in the trick, decide winner
        if len(self.current_trick) == 4:
            self.resolve_trick()
            self.current_round += 1
            if self.current_round == 13:
                self.game_over = True

    def resolve_trick(self):
        """Determine trick winner, award a trick point, and set next lead."""
        trick = self.current_trick
        lead_suit = trick[0][1]['suit']
        highest_card = None
        winner = None

        for player, card in trick:
            c_suit = card['suit']
            c_val = self.card_value(card['value'])

            if c_suit == self.trump_suit:
                # Trump beats everything else
                if (highest_card is None
                    or highest_card['suit'] != self.trump_suit
                    or (highest_card['suit'] == self.trump_suit
                        and c_val > self.card_value(highest_card['value']))):
                    highest_card = card
                    winner = player

            elif c_suit == lead_suit:
                # Among lead suit, pick highest
                if (highest_card is None
                    or highest_card['suit'] not in [lead_suit, self.trump_suit]):
                    highest_card = card
                    winner = player
                elif (highest_card['suit'] == lead_suit
                      and c_val > self.card_value(highest_card['value'])):
                    highest_card = card
                    winner = player
            else:
                # Off-suit, non-trump => likely not winning
                if highest_card is None:
                    highest_card = card
                    winner = player

        if winner:
            self.scores[winner] += 1
            # The winner leads the next trick
            winner_index = int(winner.split()[-1]) - 1
            self.current_turn = winner_index

        self.current_trick = []
        self.lead_suit = None

    def card_value(self, val):
        values = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
            "10": 10, "JACK": 11, "QUEEN": 12, "KING": 13, "ACE": 14
        }
        return values[val]
