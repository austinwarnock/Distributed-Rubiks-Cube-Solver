#!/usr/bin/env python3
"""Command-line Rubik's cube visualizer with ANSI colors."""

from __future__ import annotations

import argparse
import re
import sys
import time

from cube import Cube

ANSI = {
    "R": "\033[41m\033[30m",
    "G": "\033[42m\033[30m",
    "B": "\033[44m\033[37m",
    "Y": "\033[43m\033[30m",
    "W": "\033[47m\033[30m",
    "O": "\033[48;5;208m\033[30m",
}
RESET = "\033[0m"


def colorize_sticker(sticker: str, plain: bool = False) -> str:
    if plain or not sticker:
        return sticker
    code = ANSI.get(sticker[0], "")
    if not code:
        return sticker
    return f"{code} {sticker} {RESET}"


def render_net(cube: Cube, plain: bool = False) -> str:
    lines: list[str] = []

    def face_rows(face: str) -> list[list[str]]:
        return [list(row) for row in cube.get_face(face).squares]

    u = face_rows("U")
    l, f, r, b = (face_rows(x) for x in ("L", "F", "R", "B"))
    d = face_rows("D")

    pad = "      "
    for row in u:
        lines.append(pad + "".join(colorize_sticker(s, plain) for s in row))
    for i in range(3):
        row = (
            "".join(colorize_sticker(s, plain) for s in l[i])
            + " "
            + "".join(colorize_sticker(s, plain) for s in f[i])
            + " "
            + "".join(colorize_sticker(s, plain) for s in r[i])
            + " "
            + "".join(colorize_sticker(s, plain) for s in b[i])
        )
        lines.append(row)
    for row in d:
        lines.append(pad + "".join(colorize_sticker(s, plain) for s in row))
    return "\n".join(lines)


MOVE_TOKEN = re.compile(r"^(?P<face>[ULFRBD])(?P<prime>['’`])?$", re.IGNORECASE)


def parse_move_token(token: str) -> tuple[str, str] | None:
    token = token.strip()
    if not token:
        return None
    m = MOVE_TOKEN.match(token)
    if not m:
        raise ValueError(f"invalid move '{token}' (use U R F' etc.)")
    face = m.group("face").upper()
    direction = "counterclockwise" if m.group("prime") else "clockwise"
    return face, direction


def parse_moves(text: str) -> list[tuple[str, str]]:
    moves: list[tuple[str, str]] = []
    for raw in re.split(r"[\s,]+", text.strip()):
        if not raw:
            continue
        parsed = parse_move_token(raw)
        if parsed:
            moves.append(parsed)
    return moves


def print_status(cube: Cube, plain: bool, label: str | None = None) -> None:
    if label:
        print(f"\n{label}")
        print("-" * len(label))
    print(render_net(cube, plain=plain))
    solved = cube.is_solved()
    print(f"Solved: {'yes' if solved else 'no'}")


def interactive_loop(cube: Cube, plain: bool) -> None:
    print("Interactive mode — enter moves (U R F' …), 'show', 'scramble N', or 'quit'.")
    print_status(cube, plain, "Current cube")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        lower = line.lower()
        if lower in {"q", "quit", "exit"}:
            break
        if lower == "show":
            print_status(cube, plain)
            continue
        if lower.startswith("scramble"):
            parts = lower.split()
            n = int(parts[1]) if len(parts) > 1 else 10
            cube.scramble(n)
            print_status(cube, plain, f"Scrambled ({n} moves)")
            continue
        for face, direction in parse_moves(line):
            cube.rotate(face, direction)
        print_status(cube, plain)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Display and animate a Rubik's cube in the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Move notation: U R F L B D with optional ' for counter-clockwise.\n"
            "Examples:\n"
            "  python3 visualize.py\n"
            "  python3 visualize.py --scramble 15\n"
            "  python3 visualize.py --moves \"R U R' U'\" --step\n"
        ),
    )
    parser.add_argument("--moves", "-m", type=str, default="", help="Sequence of face turns")
    parser.add_argument("--scramble", "-s", type=int, default=0, metavar="N", help="Scramble with N random moves")
    parser.add_argument("--step", action="store_true", help="Pause between moves (use with --delay)")
    parser.add_argument("--delay", type=float, default=0.35, help="Seconds between moves when stepping")
    parser.add_argument("--plain", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive move entry")
    args = parser.parse_args(argv)

    cube = Cube()
    if args.scramble:
        cube.scramble(args.scramble)

    moves = parse_moves(args.moves)
    if not moves and not args.scramble and not args.interactive:
        print_status(cube, args.plain, "Solved cube")
        print("\nTip: try --scramble 10 or --interactive")
        return 0

    if moves:
        print_status(cube, args.plain, "Start")
        for i, (face, direction) in enumerate(moves, start=1):
            label = f"{face}{'`' if direction == 'counterclockwise' else ''}"
            if args.step:
                time.sleep(args.delay)
            cube.rotate(face, direction)
            print_status(cube, args.plain, f"After move {i}: {label}")

    if args.interactive:
        interactive_loop(cube, args.plain)
    elif moves or args.scramble:
        print_status(cube, args.plain, "Final")

    return 0


if __name__ == "__main__":
    sys.exit(main())
