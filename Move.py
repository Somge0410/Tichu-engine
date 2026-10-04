from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product

from Cards import CardColor, CardType, all_cards, beats as card_beats


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
    Pass = 25
    FourteenStraight = 26
    FourPairs = 27
    FivePairs = 28
    SixPairs = 29
    SevenPairs = 30


@dataclass(frozen=True, slots=True)
class Move:
    type: MoveType
    card_mask: int
    value_mask: int
    color_mask: int
    primary_rank: int = 0


STRAIGHT_TYPES_BY_LENGTH = {
    5: MoveType.FiveStraight,
    6: MoveType.SixStraight,
    7: MoveType.SevenStraight,
    8: MoveType.EightStraight,
    9: MoveType.NineStraight,
    10: MoveType.TenStraight,
    11: MoveType.ElevenStraight,
    12: MoveType.TwelveStraight,
    13: MoveType.ThirteenStraight,
    14: MoveType.FourteenStraight,
}

STRAIGHT_BOMB_TYPES_BY_LENGTH = {
    5: MoveType.FiveBomb,
    6: MoveType.SixBomb,
    7: MoveType.SevenBomb,
    8: MoveType.EightBomb,
    9: MoveType.NineBomb,
    10: MoveType.TenBomb,
    11: MoveType.ElevenBomb,
    12: MoveType.TwelveBomb,
    13: MoveType.ThirteenBomb,
}

PAIR_RUN_TYPES_BY_LENGTH = {
    3: MoveType.ThreePairs,
    4: MoveType.FourPairs,
    5: MoveType.FivePairs,
    6: MoveType.SixPairs,
    7: MoveType.SevenPairs,
}

BOMB_LENGTH_BY_TYPE = {
    MoveType.FourBomb: 4,
    **{
        move_type: length
        for length, move_type in STRAIGHT_BOMB_TYPES_BY_LENGTH.items()
    },
}


def _set_bit_indices(mask: int) -> Iterator[int]:
    while mask:
        lowest_set_bit = mask & -mask
        yield lowest_set_bit.bit_length() - 1
        mask ^= lowest_set_bit


def _make_move(
    move_type: MoveType,
    card_indices: Iterable[int],
    value_mask: int | None = None,
    primary_rank: int | None = None,
) -> Move:
    card_mask = 0
    actual_value_mask = 0
    color_mask = 0
    for index in card_indices:
        card = all_cards[index]
        card_mask |= 1 << index
        actual_value_mask |= card.value_mask()
        color_mask |= card.color_mask()
    return Move(
        type=move_type,
        card_mask=card_mask,
        value_mask=actual_value_mask if value_mask is None else value_mask,
        color_mask=color_mask,
        primary_rank=(
            primary_rank
            if primary_rank is not None
            else (actual_value_mask if value_mask is None else value_mask).bit_length() - 1
        ),
    )


def _append_move(moves: list[Move], seen: set[Move], move: Move) -> None:
    if move not in seen:
        seen.add(move)
        moves.append(move)


def _highest_rank(move: Move) -> int:
    return move.value_mask.bit_length() - 1


def _full_house_rank(move: Move) -> int:
    if move.primary_rank:
        return move.primary_rank
    rank_counts: dict[CardType, int] = {}
    for index in _set_bit_indices(move.card_mask):
        rank = all_cards[index].type
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    return max(
        (rank.value for rank, count in rank_counts.items() if count == 3),
        default=0,
    )


def _bomb_strength(move: Move) -> tuple[int, int] | None:
    bomb_length = BOMB_LENGTH_BY_TYPE.get(move.type)
    if bomb_length is None:
        return None
    return bomb_length, _highest_rank(move)


def beats(move1: Move, move2: Move) -> bool:
    if move1.type == MoveType.Pass:
        return False
    if move2.type == MoveType.Pass:
        return True

    bomb1 = _bomb_strength(move1)
    bomb2 = _bomb_strength(move2)
    if bomb1 is not None or bomb2 is not None:
        if bomb1 is None:
            return False
        if bomb2 is None:
            return True
        return bomb1 > bomb2

    if move1.type != move2.type:
        return False
    if move1.type == MoveType.Single:
        card1_index = next(_set_bit_indices(move1.card_mask))
        card2_index = next(_set_bit_indices(move2.card_mask))
        return card_beats(all_cards[card1_index], all_cards[card2_index])
    if move1.type == MoveType.FullHouse:
        return _full_house_rank(move1) > _full_house_rank(move2)
    return _highest_rank(move1) > _highest_rank(move2)


def _generate_pair_runs(
    hand_mask: int,
    moves: list[Move],
    seen: set[Move],
) -> None:
    cards_by_rank: dict[int, list[int]] = {}
    for index in _set_bit_indices(hand_mask):
        rank = all_cards[index].type.value
        if CardType.Two.value <= rank <= CardType.Ace.value:
            cards_by_rank.setdefault(rank, []).append(index)

    pair_options = {
        rank: tuple(combinations(cards_by_rank.get(rank, []), 2))
        for rank in range(CardType.Two.value, CardType.Ace.value + 1)
    }
    max_length = min(7, hand_mask.bit_count() // 2)
    for length, move_type in PAIR_RUN_TYPES_BY_LENGTH.items():
        if length > max_length:
            continue
        for start in range(
            CardType.Two.value,
            CardType.Ace.value - length + 2,
        ):
            rank_options = [pair_options[rank] for rank in range(start, start + length)]
            if any(not options for options in rank_options):
                continue
            for selected_pairs in product(*rank_options):
                card_indices = (
                    index
                    for pair in selected_pairs
                    for index in pair
                )
                _append_move(moves, seen, _make_move(move_type, card_indices))


def _append_full_house(
    moves: list[Move],
    seen: set[Move],
    card_indices: Iterable[int],
    triplet_rank: int,
    pair_rank: int,
) -> None:
    value_mask = (1 << triplet_rank) | (1 << pair_rank)
    _append_move(
        moves,
        seen,
        _make_move(
            MoveType.FullHouse,
            card_indices,
            value_mask=value_mask,
            primary_rank=triplet_rank,
        ),
    )


def _generate_phoenix_pairs_and_triples(
    cards_by_rank: dict[int, list[int]],
    phoenix_indices: list[int],
    moves: list[Move],
    seen: set[Move],
) -> None:
    for phoenix_index in phoenix_indices:
        for rank, rank_cards in cards_by_rank.items():
            rank_mask = 1 << rank
            for card_index in rank_cards:
                _append_move(
                    moves,
                    seen,
                    _make_move(
                        MoveType.Pair,
                        (card_index, phoenix_index),
                        value_mask=rank_mask,
                        primary_rank=rank,
                    ),
                )
            for selected in combinations(rank_cards, 2):
                _append_move(
                    moves,
                    seen,
                    _make_move(
                        MoveType.ThreeOfAKind,
                        (*selected, phoenix_index),
                        value_mask=rank_mask,
                        primary_rank=rank,
                    ),
                )


def _generate_full_houses(
    cards_by_rank: dict[int, list[int]],
    phoenix_indices: list[int],
    moves: list[Move],
    seen: set[Move],
) -> None:
    ranks = range(CardType.Two.value, CardType.Ace.value + 1)
    for triplet_rank in ranks:
        triplet_cards = cards_by_rank.get(triplet_rank, [])
        for pair_rank in ranks:
            if pair_rank == triplet_rank:
                continue
            pair_cards = cards_by_rank.get(pair_rank, [])

            if len(triplet_cards) >= 3 and len(pair_cards) >= 2:
                for triplet in combinations(triplet_cards, 3):
                    for pair in combinations(pair_cards, 2):
                        _append_full_house(
                            moves,
                            seen,
                            (*triplet, *pair),
                            triplet_rank,
                            pair_rank,
                        )

            for phoenix_index in phoenix_indices:
                if len(triplet_cards) >= 2 and len(pair_cards) >= 2:
                    for triplet in combinations(triplet_cards, 2):
                        for pair in combinations(pair_cards, 2):
                            _append_full_house(
                                moves,
                                seen,
                                (*triplet, *pair, phoenix_index),
                                triplet_rank,
                                pair_rank,
                            )
                if len(triplet_cards) >= 3 and len(pair_cards) >= 1:
                    for triplet in combinations(triplet_cards, 3):
                        for pair in combinations(pair_cards, 1):
                            _append_full_house(
                                moves,
                                seen,
                                (*triplet, *pair, phoenix_index),
                                triplet_rank,
                                pair_rank,
                            )


def _generate_straights(
    hand_mask: int,
    moves: list[Move],
    seen: set[Move],
) -> None:
    cards_by_rank: dict[int, list[int]] = {}
    phoenix_indices = []
    for index in _set_bit_indices(hand_mask):
        card_type = all_cards[index].type
        if CardType.MahJong.value <= card_type.value <= CardType.Ace.value:
            cards_by_rank.setdefault(card_type.value, []).append(index)
        elif card_type == CardType.Phoenix:
            phoenix_indices.append(index)

    low_rank = CardType.MahJong.value
    high_rank = CardType.Ace.value
    for length, straight_type in STRAIGHT_TYPES_BY_LENGTH.items():
        for start in range(low_rank, high_rank - length + 2):
            ranks = range(start, start + length)
            rank_options = [cards_by_rank.get(rank, []) for rank in ranks]
            sequence_value_mask = 0
            for rank in ranks:
                sequence_value_mask |= 1 << rank

            if all(rank_options):
                for card_indices in product(*rank_options):
                    colors = [all_cards[index].color for index in card_indices]
                    move_type = straight_type
                    if (
                        colors[0] != CardColor.NoColor
                        and all(color == colors[0] for color in colors)
                    ):
                        move_type = STRAIGHT_BOMB_TYPES_BY_LENGTH.get(
                            length,
                            straight_type,
                        )
                    _append_move(
                        moves,
                        seen,
                        _make_move(move_type, card_indices),
                    )

            for phoenix_index in phoenix_indices:
                for wild_rank in ranks:
                    other_rank_options = [
                        cards_by_rank.get(rank, [])
                        for rank in ranks
                        if rank != wild_rank
                    ]
                    if any(not options for options in other_rank_options):
                        continue
                    for other_cards in product(*other_rank_options):
                        card_indices = (*other_cards, phoenix_index)
                        _append_move(
                            moves,
                            seen,
                            _make_move(
                                straight_type,
                                card_indices,
                                value_mask=sequence_value_mask,
                            ),
                        )


def generate_valid_moves(hand_mask: int) -> list[Move]:
    moves: list[Move] = []
    seen: set[Move] = set()
    cards_by_type: dict[CardType, list[int]] = {}
    for index in _set_bit_indices(hand_mask):
        card_type = all_cards[index].type
        cards_by_type.setdefault(card_type, []).append(index)

    for card_type, card_indices in cards_by_type.items():
        for index in card_indices:
            _append_move(moves, seen, _make_move(MoveType.Single, [index]))
        for selected in combinations(card_indices, 2):
            _append_move(moves, seen, _make_move(MoveType.Pair, selected))
        for selected in combinations(card_indices, 3):
            _append_move(
                moves,
                seen,
                _make_move(MoveType.ThreeOfAKind, selected),
            )
        if (
            CardType.Two.value <= card_type.value <= CardType.Ace.value
            and len(card_indices) == 4
        ):
            _append_move(
                moves,
                seen,
                _make_move(MoveType.FourBomb, card_indices),
            )

    cards_by_rank = {
        card_type.value: card_indices
        for card_type, card_indices in cards_by_type.items()
        if CardType.Two.value <= card_type.value <= CardType.Ace.value
    }
    phoenix_indices = cards_by_type.get(CardType.Phoenix, [])
    _generate_phoenix_pairs_and_triples(
        cards_by_rank,
        phoenix_indices,
        moves,
        seen,
    )
    _generate_full_houses(cards_by_rank, phoenix_indices, moves, seen)
    _generate_pair_runs(hand_mask, moves, seen)
    _generate_straights(hand_mask, moves, seen)
    return moves

def legal_moves(hand_mask: int, previous_move: Move | None, needs_to_be_bomb: bool) -> list[Move]:
    all_moves = generate_valid_moves(hand_mask)
    if previous_move is None:
        return all_moves
    return [move for move in all_moves if beats(move, previous_move) and (not needs_to_be_bomb or move.type in 
                                                                          {MoveType.FourBomb, MoveType.FiveBomb, MoveType.SixBomb,
                                                                           MoveType.SevenBomb,MoveType.EightBomb,MoveType.NineBomb,
                                                                           MoveType.TenBomb, MoveType.ElevenBomb, MoveType.TwelveBomb,
                                                                           MoveType.ThirteenBomb})]