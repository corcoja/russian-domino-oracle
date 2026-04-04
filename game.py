import math
from typing import List, Tuple


class Game:

    def __init__(self,
                 table: List[Tuple[int, int]],
                 my_hand: List[Tuple[int, int]],
                 opponent_hand_size: int,
                 stock_size: int):
        self.__table = table
        self.__my_hand = my_hand
        self.__opponent_hand_size = opponent_hand_size
        self.__stock_size = stock_size

    @property
    def table(self):
        return self.__table

    @property
    def my_hand(self):
        return self.__my_hand

    @property
    def opponent_hand_size(self):
        return self.__opponent_hand_size

    @property
    def stock_size(self):
        return self.__stock_size

    def me_draw_from_stock(self, piece: Tuple[int, int]):
        self.__my_hand.append(piece)
        self.__stock_size = self.__stock_size - 1

    def opponent_draw_from_stock(self):
        self.__opponent_hand_size = self.__opponent_hand_size + 1
        self.__stock_size = self.__stock_size - 1

    def opponent_added_piece(self):
        self.__opponent_hand_size = self.__opponent_hand_size - 1

    def add_piece_on_left(self, piece: Tuple[int, int]):
        if not self.__table or self.__table[0][0] == piece[1]:
            self.__table.insert(0, piece)
        elif self.__table[0][0] == piece[0]:
            self.__table.insert(0, piece[::-1])
        else:
            raise ValueError(
                "Piece numbers are invalid for current leftmost piece in the snake!")

    def add_piece_on_right(self, piece: Tuple[int, int]):
        if not self.__table or self.__table[-1][1] == piece[0]:
            self.__table.append(piece)
        elif self.__table[-1][1] == piece[1]:
            self.__table.append(piece[::-1])
        else:
            raise ValueError(
                "Piece numbers are invalid for current rightmost piece in the snake!")

    def add_to_my_hand(self, piece: Tuple[int, int]) -> Tuple[int, int]:
        self.__my_hand.append(piece)
        return self.__my_hand[-1]

    def remove_from_my_hand(self, index: int) -> Tuple[int, int]:
        try:
            return self.__my_hand.pop(index)
        except IndexError as e:
            raise ValueError("Invalid index!") from e

    def opponent_stats(self) -> dict[int: float]:
        return {i: self.__piece_probability(i)
                for i in range(6 + 1)}

    def __piece_probability(self, piece_no: int) -> float:
        pieces_left = max(
            0, 7 - sum(piece_no in piece for piece in self.__table + self.__my_hand))
        total_ways = math.comb(self.__opponent_hand_size +
                               self.__stock_size, pieces_left)
        return 1 - math.comb(self.__stock_size, pieces_left) / total_ways

    def __str__(self) -> str:
        return (
            f"Stock size is {self.__stock_size}.\n"
            f"Oppenent has {self.__opponent_hand_size} pieces.\n"
            f"Current table:\n\t{self.__table}\n"
            f"Your hand is:\n\t{self.__my_hand}\n"
            f"Indices: {''.join(f'{i:4d}    ' for i in range(len(self.__my_hand)))}\n"
            f"Opponent Stats:\n\t{self.opponent_stats()}\n"
        )
