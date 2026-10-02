from enum import Enum

from transforms import (
    FACE_ORDER,
    apply_move,
    solved_state,
    stickers_from_string,
    stringify_state,
)


class Color(Enum):
    RED = "R"
    GREEN = "G"
    BLUE = "B"
    YELLOW = "Y"
    WHITE = "W"
    ORANGE = "O"


COLOR_MAP = {
    "U": Color.YELLOW,
    "L": Color.BLUE,
    "F": Color.RED,
    "R": Color.GREEN,
    "B": Color.ORANGE,
    "D": Color.WHITE,
}


class Face:
    def __init__(self, color: Color):
        self.color = color
        self.squares = [[f"{color.value}{(r * 3) + c + 1}" for c in range(3)] for r in range(3)]

    def set_row(self, row: int, squares: list):
        if len(squares) != 3:
            raise ValueError("squares must be a list of length 3")
        self.squares[row] = list(squares)

    def set_column(self, column: int, squares: list):
        if len(squares) != 3:
            raise ValueError("squares must be a list of length 3")
        for i in range(3):
            self.squares[i][column] = squares[i]

    def rotate(self, direction: str):
        s = self.squares
        if direction == "clockwise":
            self.squares = [
                [s[2][0], s[1][0], s[0][0]],
                [s[2][1], s[1][1], s[0][1]],
                [s[2][2], s[1][2], s[0][2]],
            ]
        elif direction == "counterclockwise":
            self.squares = [
                [s[0][2], s[1][2], s[2][2]],
                [s[0][1], s[1][1], s[2][1]],
                [s[0][0], s[1][0], s[2][0]],
            ]
        else:
            raise ValueError("direction must be 'clockwise' or 'counterclockwise'")

    def get_row(self, row: int):
        return self.squares[row]

    def get_column(self, column: int):
        return [row[column] for row in self.squares]

    def get_row_for_print(self, row: int):
        return "|".join(str(s) for s in self.squares[row])

    def __str__(self):
        out = ""
        for row in self.squares:
            out += "|"
            for square in row:
                out += str(square) + "|"
            out += "\n"
        return out


class Cube:
    def __init__(self, state: str = None):
        self.faces = {
            "U": Face(Color.YELLOW),
            "L": Face(Color.BLUE),
            "F": Face(Color.RED),
            "R": Face(Color.GREEN),
            "B": Face(Color.ORANGE),
            "D": Face(Color.WHITE),
        }
        self._stickers = solved_state()
        if state:
            self.parse(state)
        else:
            self._sync_faces_from_stickers()

    def _sync_faces_from_stickers(self) -> None:
        idx = 0
        for face in FACE_ORDER:
            squares = self.faces[face].squares
            for r in range(3):
                for c in range(3):
                    squares[r][c] = self._stickers[idx]
                    idx += 1

    def get_face(self, face: str):
        if face not in self.faces:
            raise ValueError("face must be one of 'U', 'L', 'F', 'R', 'B', 'D'")
        return self.faces[face]

    def rotate(self, face: str, direction: str):
        if face not in self.faces:
            raise ValueError("face must be one of 'U', 'L', 'F', 'R', 'B', 'D'")
        if direction not in ("clockwise", "counterclockwise"):
            raise ValueError("direction must be 'clockwise' or 'counterclockwise'")
        apply_move(self._stickers, face, direction)
        self._sync_faces_from_stickers()

    def print_move(self, face: str, direction: str):
        print(f"{face}{'`' if direction == 'counterclockwise' else ''}")

    def scramble(self, max_moves: int = 5):
        from random import choice

        for _ in range(max_moves):
            face = choice(list(self.faces.keys()))
            direction = choice(["clockwise", "counterclockwise"])
            self.rotate(face, direction)

    def stringify(self):
        return stringify_state(self._stickers)

    def parse(self, input_str: str):
        self._stickers = stickers_from_string(input_str)
        self._sync_faces_from_stickers()

    def is_solved(self):
        for face in FACE_ORDER:
            color = self.get_face(face).color.value
            for row in range(3):
                for col in range(3):
                    expected = color + str((row * 3) + col + 1)
                    if self.get_face(face).squares[row][col] != expected:
                        return False
        return True

    def __str__(self):
        out = ""
        for i in range(3):
            out += "         " + str(self.faces["U"].get_row_for_print(i)) + "\n"
        for i in range(3):
            out += str(self.faces["L"].get_row_for_print(i)) + "|"
            out += str(self.faces["F"].get_row_for_print(i)) + "|"
            out += str(self.faces["R"].get_row_for_print(i)) + "|"
            out += str(self.faces["B"].get_row_for_print(i)) + "\n"
        for i in range(3):
            out += "         " + str(self.faces["D"].get_row_for_print(i)) + "\n"
        return out + "\n"


if __name__ == "__main__":
    pass
