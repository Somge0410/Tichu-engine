from enum import Enum, auto
from dataclasses import dataclass
class CardColor(Enum):
    Green = auto()
    Red = auto()
    Blue = auto()
    Black= auto()
    NoColor= auto()

class CardType(Enum):
    Dog =0
    MahJong=1
    Two=2
    Three=3
    Four=4
    Five=5
    Six=6
    Seven=7
    Eight=8
    Nine=9
    Ten=10
    Jack=11
    Queen=12
    King=13
    Ace=14
    Phoenix=16
    Dragon=17
@dataclass
class Card:
    color: CardColor
    type: CardType
    def value_mask(self) -> int:
        return 1 << self.type.value

    def color_mask(self) -> int:
        return 1 << self.color.value


standard_types = (
    CardType.Two,
    CardType.Three,
    CardType.Four,
    CardType.Five,
    CardType.Six,
    CardType.Seven,
    CardType.Eight,
    CardType.Nine,
    CardType.Ten,
    CardType.Jack,
    CardType.Queen,
    CardType.King,
    CardType.Ace,
)

special_types = (
    CardType.MahJong,
    CardType.Dog,
    CardType.Phoenix,
    CardType.Dragon,
)
def beats(card1: Card, card2: Card) -> bool:
    if card1.type == CardType.Dog:
        return False
    if card2.type == CardType.Dog:
        return True
    if card1.type == CardType.Phoenix:
        return not card2.type == CardType.Dragon
    if card2.type == CardType.Phoenix:
        return True
    if card1.type == CardType.Dragon:
        return True
    if card2.type == CardType.Dragon:
        return False
    return card1.type.value > card2.type.value
all_cards = (
    [Card(color, type) for color in CardColor if color != CardColor.NoColor for type in standard_types]
    + [Card(CardColor.NoColor, type) for type in special_types]
)
