from Move import Move, MoveType
from player import Player, Location
from dataclasses import field
from Cards import all_cards
from enum import Enum

import player

class GlobbalLocation(Enum):
    Unkown = 0
    Player1 = 1
    Player2 = 2
    Player3 = 3
    Player4 = 4
    Bank1 = 5
    Bank2 = 6
    Bank3 = 7
    Bank4 = 8
    table = 9

class Game:
    current_player: int =0
    top_move: Move = None
    top_player: int = None
    score: int = 0
    team1_score: int = 0
    team2_score: int = 0
    round_winner: str = None
    amount_of_pass: int = 0
    tichu_mask: int = 0
    grand_tichu_mask: int = 0
    team1_player_with_cards: int = 0
    team2_player_with_cards: int = 0
    def __init__(self,):
        self.players = [Player(i, 0) for i in range(1, 5)]
        self.deck: list[Location] = [GlobbalLocation.Unkown] * len(all_cards)

    def give_eight_cards(self, player: Player):
        available_indices = [i for i, location in enumerate(self.deck) if location == Location.Unkown]
        for _ in range(8):
            for i in available_indices:
                self.deck[i] = player.location
                player.receive_card(i)
                available_indices.remove(i)
                break

    def give_six_cards(self, player: Player):
        available_indices = [i for i, location in enumerate(self.deck) if location == Location.Unkown]
        for _ in range(6):
            for i in available_indices:
                self.deck[i] = player.location
                player.receive_card(i)
                available_indices.remove(i)
                break
    def ask_player_for_tichu(self, player: Player) -> bool:
        return player.ask_for_tichu()
    def ask_player_for_bomb(self, player: Player) -> bool:
        return player.ask_for_bomb()
    def ask_player_for_move(self, player: Player, needs_to_bomb: bool=False) -> Move:
        needs_to_bomb = self.top_move.type== MoveType.Bomb or self.top_move.type== MoveType.Dragon or player!=self.current_player

        return player.ask_for_move(top_move=self.top_move, needs_to_bomb=needs_to_bomb)
    def update_game_after_move(self, move: Move, update_pass: bool = True):
        if move.type==MoveType.Pass:
            if update_pass:
                self.amount_of_pass += 1
            self.current_player = (self.current_player + 1) % 4
            if self.amount_of_pass >= 3 and update_pass:
                self.round_winner = f"Player {self.current_player}"
                self.amount_of_pass = 0
                for index in range(len(self.deck)):
                    if self.deck[index] == GlobbalLocation.table:
                        self.deck[index] = GlobbalLocation.Player1 + self.current_player % 4
                        for player in self.players:
                            player.notify_of_banking(index, self.current_player)

        self.top_move = move
        self.top_player = self.current_player
        for player in self.players:
            player.notify_of_move(move, self.current_player)
    def play_round(self):
        while self.team1_score < 1000 and self.team2_score < 1000:
            self.tichu_mask = 0
            self.grand_tichu_mask = 0
            self.current_player = None
            self.top_move = None
            self.top_player = None
            self.round_winner = None
            self.amount_of_pass = 0

            for player in self.players:
                self.give_eight_cards(player)
                grand_tichu_called = self.ask_player_for_grand_tichu(player)
                if grand_tichu_called:
                    self.grand_tichu_mask |= 1 << (player.get_id() - 1)
                    for other_player in self.players:
                        other_player.notify_of_grand_tichu(player.get_id())

            for player in self.players:
                self.give_six_cards(player)
                tichu_called = self.ask_player_for_tichu(player)
                if tichu_called:
                    self.tichu_mask |= 1 << (player.get_id() - 1)
                    for other_player in self.players:
                        other_player.notify_of_tichu(player.get_id())

            trade = []
            for player in self.players:
                trade.append(player.ask_for_trade())
            for id, card_index in enumerate(trade):
                self.players[id].receive_card(card_index)

            mahjong_index = all_cards.index("Mahjong")
            for player in self.players:
                if player.get_id() == self.deck[mahjong_index]:
                    current_player = player.get_id()
                    self.current_player = current_player

            round_running = True
            while round_running:
                if self.team1_player_with_cards < 1 or self.team2_player_with_cards < 1:
                    round_running = False
                    self.score_round()
                    break

                move = self.ask_player_for_move(self.players[self.current_player])
                self.update_game_after_move(move)
                passers_after_move = 0

                while passers_after_move < 3:
                    move = self.ask_player_for_move(
                        self.players[(self.current_player + 1 + passers_after_move) % 4],
                        needs_to_bomb=True,
                    )
                    self.update_game_after_move(move)
                    if move.type == MoveType.Pass:
                        passers_after_move += 1
                    else:
                        passers_after_move = 0