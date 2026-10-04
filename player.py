from enum import Enum, auto
import Move
from Move import legal_moves, _set_bit_indeces
from cards import all_cards
from dataclasses import dataclass, field
class Location(Enum):
    Hand = 1
    NextOPHand = 2
    PrevOPHand = 3
    TeamMate_Hand = 4
    Table = 5
    Unkown = 6
    My_Bank = 7
    NextOPBank = 8
    PrevOPBank = 9
    TeamMate_Bank = 10
@dataclass
class Player:
    id: int
    score: int
    deck: list[Location] =field(default_factory=lambda : [Location.Unkown]*len(all_cards))
    hand_mask: int = 0
    top_move: Move.Move
    top_player: int = None
    def receive_card(self, index:int):
        self.deck[index] = Location.Hand
        self.hand_mask |= 1 << index
    def take_card_away(self, index:int, player_id:int):
        if self.deck[index] == Location.Hand:
            self.hand_mask &= ~(1 << index)
        self.deck[index] = Location.My_Bank.value + (self.id + player_id) % 4
    def play_card(self, index:int):
        self.deck[index] = Location.Table
        self.hand_mask &= ~(1 << index)
    def move_cards_to_bank(self, player_id: int):
        player_index=Location.My_Bank.value+(self.id+player_id)%4
        for i in range(len(self.deck)):
            if self.deck[i] == Location.Table:
                self.deck[i] = Location(player_index)
    def give_card_to_player(self, index:int, player_id:int):
        if self.deck[index] != Location.Hand:
            return
        self.deck[index] = Location.Hand.value+(self.id+player_id)%4
    def notify_of_banking(self, index: int, player_id: int):
        
        if self.deck[index] == Location.Hand:
            self.hand_mask |= 1 << index
        else:
            self.hand_mask &= ~(1 << index)
        new_location = Location.My_Bank.value + (self.id + player_id) % 4
        self.deck[index] = Location(new_location)
    def notify_of_move(self, move: Move.Move, player_id: int):
        self.top_move = move
        self.top_player = (self.id+player_id)%4
        for i in _set_bit_indeces(move.mask):
            self.deck[i] = Location.My_Bank.value + (self.id + player_id) % 4
    def ask_for_tichu(self) -> bool:
        # Implement the logic for asking for Tichu here
        return False
    def ask_for_bomb(self) -> bool:
        # Implement the logic for asking for Bomb here
        return False
    def ask_for_move(self, top_move: Move.Move = None, needs_to_bomb: bool = False) -> Move.Move:
        moves=legal_moves(self.deck, self.hand_mask)
        # Implement the logic for asking for a move here
        return moves[0] if moves else None
    def get_id(self) -> int:
        return self.id
    def ask_for_trade(self) -> list[int]:
        # Implement the logic for asking for a trade here
        return []
    
    
