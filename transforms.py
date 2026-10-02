"""Fast sticker-level matrix transforms for the Rubik's cube."""

from __future__ import annotations

from move_permutations import MOVE_PERMUTATIONS

Sticker = str
State = list[Sticker]

FACE_ORDER = ("U", "L", "F", "R", "B", "D")
MOVE_KEYS = tuple(MOVE_PERMUTATIONS.keys())


def apply_move(state: State, face: str, direction: str) -> None:
    """Apply a face turn in-place using a precomputed permutation."""
    perm = MOVE_PERMUTATIONS[(face, direction)]
    src = state
    snapshot = src[:]
    for i, j in enumerate(perm):
        src[i] = snapshot[j]


def apply_move_copy(state: State, face: str, direction: str) -> State:
    perm = MOVE_PERMUTATIONS[(face, direction)]
    snapshot = state
    return [snapshot[j] for j in perm]


def compose_permutation(first: tuple[int, ...], second: tuple[int, ...]) -> tuple[int, ...]:
    """Return permutation equivalent to applying first, then second."""
    return tuple(first[second[i]] for i in range(len(first)))


def stringify_state(state: State) -> str:
    return "".join(state)


def stickers_from_string(s: str) -> State:
    if len(s) != 108:
        raise ValueError("cube state string must be 108 characters (54 stickers)")
    return [s[i : i + 2] for i in range(0, 108, 2)]


def solved_state() -> State:
    state: State = []
    for face in FACE_ORDER:
        color = {"U": "Y", "L": "B", "F": "R", "R": "G", "B": "O", "D": "W"}[face]
        for i in range(1, 10):
            state.append(f"{color}{i}")
    return state
