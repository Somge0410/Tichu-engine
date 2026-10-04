
from dataclasses import dataclass
from enum import auto, Enum
from Cards import CardType
from cards import all_cards, beats, Color

class MoveType(Enum):
    Single = 1
    Pair = 2
    ThreeOfAKind = 3
    FullHouse = 4
    ThreePairs = 5
    FiveStraight = 6
    SixStraight = 7
    SevenStraight = 8
    EightStraight = 9
    NineStraight = 10
    TenStraight = 11
    ElevenStraight = 12
    TwelveStraight = 13
    ThirteenStraight = 14
    FourBomb = 15
    FiveBomb = 16
    SixBomb = 17
    SevenBomb = 18
    EightBomb = 19
    NineBomb = 20
    TenBomb = 21
    ElevenBomb = 22
    TwelveBomb = 23
    ThirteenBomb = 24
    Pass=25

@dataclass(frozen=True,slots=True)
class Move:
    type: MoveType
    card_mask: int
    value_mask: int
    color_mask: int
def beats(move1: Move, move2: Move) -> bool:
    if move1.type == MoveType.Pass:
        return True
    if move1.type != move2.type:
        if move1.type<MoveType.FourBomb:
            return False
        if move1.type > move2.type:
            return True
        return False
    if(move1.type in {MoveType.Single, MoveType.Pair, MoveType.ThreeOfAKind, MoveType.FourBomb}):
        card1=all_cards[move1.card_mask.highest_bit()]
        card2=all_cards[move2.card_mask.highest_bit()]
        return beats(card1, card2)
    if(move1.type==MoveType.FullHouse):
        card1=all_cards[move1.card_mask.highest_bit()]
        card2=all_cards[move2.card_mask.highest_bit()]
        for i in range(move1.card_mask.bit_length()):
            if move1.card_mask & (1 << i):
                if beats(all_cards[i], card1):
                    card1=all_cards[i]
                    break
        for i in range(move2.card_mask.bit_length()):
            if move2.card_mask & (1 << i):
                if beats(all_cards[i], card2):
                    card2=all_cards[i]
                    break
        return beats(card1, card2)
    card1=all_cards[move1.card_mask.highest_bit()]
    card2=all_cards[move2.card_mask.highest_bit()]
    for i in range(move1.card_mask.bit_length()):
        if move1.card_mask & (1 << i):
            if beats(all_cards[i], card1):
                card1=all_cards[i]
    for i in range(move2.card_mask.bit_length()):
        if move2.card_mask & (1 << i):
            if beats(all_cards[i], card2):
                card2=all_cards[i]
    return beats(card1, card2)

def generate_valid_moves(hand_mask: int) -> list[Move]:
    moves = []
    for type in CardType:
        card_indices = [i for i in range(hand_mask.bit_length()) if hand_mask & (1 << i) and all_cards[i].type == type]
        for index in card_indices:
            moves.append(Move(type=MoveType.Single, card_mask=1 << index, value_mask=all_cards[index].value_mask(), color_mask=all_cards[index].color_mask()))
        for i in range(len(card_indices)):
            for j in range(i + 1, len(card_indices)):
                moves.append(Move(type=MoveType.Pair, card_mask=(1 << card_indices[i]) | (1 << card_indices[j]), value_mask=all_cards[card_indices[i]].value_mask() | all_cards[card_indices[j]].value_mask(), color_mask=all_cards[card_indices[i]].color_mask() | all_cards[card_indices[j]].color_mask()))
                for k in range(j + 1, len(card_indices)):
                    moves.append(Move(type=MoveType.ThreeOfAKind, card_mask=(1 << card_indices[i]) | (1 << card_indices[j]) | (1 << card_indices[k]), value_mask=all_cards[card_indices[i]].value_mask() | all_cards[card_indices[j]].value_mask() | all_cards[card_indices[k]].value_mask(), color_mask=all_cards[card_indices[i]].color_mask() | all_cards[card_indices[j]].color_mask() | all_cards[card_indices[k]].color_mask()))
        if len(card_indices) >= 4:
            moves.append(Move(type=MoveType.FourBomb, card_mask=(1 << card_indices[0]) | (1 << card_indices[1]) | (1 << card_indices[2]) | (1 << card_indices[3]), value_mask=all_cards[card_indices[0]].value_mask() | all_cards[card_indices[1]].value_mask() | all_cards[card_indices[2]].value_mask() | all_cards[card_indices[3]].value_mask(), color_mask=all_cards[card_indices[0]].color_mask() | all_cards[card_indices[1]].color_mask() | all_cards[card_indices[2]].color_mask() | all_cards[card_indices[3]].color_mask()))
    for move_index in range(len(moves)):
        move = moves[move_index]
        if move.type == MoveType.Pair:
            for other_move_index in range(move_index + 1, len(moves)):
                other_move = moves[other_move_index]
                if other_move.type == MoveType.Pair and other_move.card_mask & move.card_mask == 0:
                    value=move.value_mask.bit_length()
                    other_value=other_move.value_mask.bit_length()
                    if abs(value - other_value) == 1:
                        combined_card_mask = move.card_mask | other_move.card_mask
                        combined_value_mask = move.value_mask | other_move.value_mask
                        combined_color_mask = move.color_mask | other_move.color_mask
                        moves.append(Move(type=MoveType.TwoPairs, card_mask=combined_card_mask, value_mask=combined_value_mask, color_mask=combined_color_mask))
                        for k in range(other_move_index + 1, len(moves)):
                            third_move = moves[k]
                            if third_move.type == MoveType.Pair and third_move.card_mask & combined_card_mask == 0:
                                third_value = third_move.value_mask.bit_length()
                                if third_value==other_value or third_value==value:
                                    continue
                                if abs(third_value - value) == 1 and abs(third_value - other_value) == 1:
                                    combined_card_mask_3 = combined_card_mask | third_move.card_mask
                                    combined_value_mask_3 = combined_value_mask | third_move.value_mask
                                    combined_color_mask_3 = combined_color_mask | third_move.color_mask
                                    moves.append(Move(type=MoveType.ThreePairs, card_mask=combined_card_mask_3, value_mask=combined_value_mask_3, color_mask=combined_color_mask_3))

                if other_move.type == MoveType.ThreePairs:
                    combined_card_mask = move.card_mask | other_move.card_mask
                    combined_value_mask = move.value_mask | other_move.value_mask
                    combined_color_mask = move.color_mask | other_move.color_mask
                    moves.append(Move(type=MoveType.FourPairs, card_mask=combined_card_mask, value_mask=combined_value_mask, color_mask=combined_color_mask))
    return moves