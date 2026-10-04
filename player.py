from enum import Enum, auto
import Move
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
    def receive_card(self, index:int):
        self.deck[index] = Location.Hand
        self.hand_mask |= 1 << index

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

    

    
    
