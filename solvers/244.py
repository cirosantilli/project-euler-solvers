#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0244.cpp"""
import sys

RED = "r"
BLUE = "b"
EMPTY = "."

MOVE_UP = 85
MOVE_LEFT = 76
MOVE_DOWN = 68
MOVE_RIGHT = 82

MOD = 100000007
SIZE = 4


class Board:
    def __init__(self, pieces="", checksum=0):
        self.pieces = pieces
        self.checksum = checksum

    def is_valid(self):
        return len(self.pieces) == SIZE * SIZE

    def __eq__(self, other):
        return self.pieces == other.pieces

    def move(self, move):
        if not self.pieces:
            return None

        index = self.pieces.find(EMPTY)
        if index < 0:
            return None

        from_x = index % SIZE
        from_y = index // SIZE

        to_x = from_x
        to_y = from_y

        if move == MOVE_UP:
            if from_y == SIZE - 1:
                return None
            to_y += 1
        elif move == MOVE_DOWN:
            if from_y == 0:
                return None
            to_y -= 1
        elif move == MOVE_LEFT:
            if from_x == SIZE - 1:
                return None
            to_x += 1
        elif move == MOVE_RIGHT:
            if from_x == 0:
                return None
            to_x -= 1
        else:
            return None

        next_index = to_y * SIZE + to_x
        new_pieces = list(self.pieces)
        new_pieces[index], new_pieces[next_index] = (
            new_pieces[next_index],
            new_pieces[index],
        )

        new_checksum = (self.checksum * 243 + move) % MOD
        return Board("".join(new_pieces), new_checksum)


def search(final_board):
    todo = [Board(".rbbrrbbrrbbrrbb")]
    history = set()
    result = 0

    last_iteration = False
    while not last_iteration:
        next_level = []

        for current in todo:
            if current == final_board:
                last_iteration = True
                result += current.checksum

            for move in (MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN):
                moved = current.move(move)
                if (
                    moved is not None
                    and moved.is_valid()
                    and moved.pieces not in history
                ):
                    next_level.append(moved)
                    history.add(moved.pieces)

        todo = next_level

    return result


def checksum_for_moves(moves: str) -> int:
    checksum = 0
    for move in moves:
        checksum = (checksum * 243 + ord(move)) % MOD
    return checksum


def main():
    final_position = ".brbbrbrrbrbbrbr"

    num_red = final_position.count(RED)
    num_blue = final_position.count(BLUE)
    num_empty = final_position.count(EMPTY)
    num_invalid = len(final_position) - num_red - num_blue - num_empty

    if num_red != 7 or num_blue != 8 or num_empty != 1 or num_invalid != 0:
        sys.exit(1)

    assert checksum_for_moves("LULUR") == 19761398
    print(search(Board(final_position)))


if __name__ == "__main__":
    main()
