from collections import deque

from cube import Cube
from random import choice
from transforms import apply_move_copy, stickers_from_string, stringify_state

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None


class IDA_star:
    def __init__(self, heuristic, max_depth: int = 20):
        self.heuristic = heuristic
        self.max_depth = max_depth
        self.threshold = max_depth
        self.min_threshold = None
        self.moves = []

    def run(self, state):
        while True:
            status = self.search(state, 1)
            if status:
                return self.moves
            self.moves = []
            self.threshold = self.min_threshold

    def check_threshold(self, cube: Cube, g):
        if cube.is_solved():
            return True
        if g >= self.threshold:
            return False
        return None

    def search(self, state, g):
        cube = Cube(state)

        current_threshold = self.check_threshold(cube, g)
        if current_threshold:
            return current_threshold

        min_val = float("inf")
        best_action = []

        for face, direction in [
            (face, direction)
            for face in ["U", "L", "F", "R", "B", "D"]
            for direction in ["clockwise", "counterclockwise"]
        ]:
            cube = Cube(state)
            cube.rotate(face, direction)

            if cube.is_solved():
                self.moves.append((face, direction))
                return True

            cube_str = cube.stringify()
            h_score = self.heuristic.get(cube_str, self.max_depth)
            f_score = g + h_score

            if f_score < min_val:
                min_val = f_score
                best_action = [(cube_str, (face, direction))]
            elif f_score == min_val:
                best_action.append((cube_str, (face, direction)))

        if best_action:
            if self.min_threshold is None or min_val < self.min_threshold:
                self.min_threshold = min_val
            next_action = choice(best_action)
            self.moves.append(next_action[1])
            status = self.search(next_action[0], g + 1)
            if status:
                return status
        return False


def build_heuristic_db(state, actions, max_moves=20, heuristic=None):
    if heuristic is None:
        heuristic = {state: 0}

    queue = deque([(stickers_from_string(state), 0)])
    progress = tqdm(desc="Heuristic DB", unit="state") if tqdm else None

    while queue:
        stickers, depth = queue.popleft()
        state_key = stringify_state(stickers)
        if heuristic.get(state_key, 10**9) < depth:
            continue
        if depth >= max_moves:
            continue

        for face, direction in actions:
            nxt = apply_move_copy(stickers, face, direction)
            nxt_key = stringify_state(nxt)
            new_depth = depth + 1
            if nxt_key not in heuristic or heuristic[nxt_key] > new_depth:
                heuristic[nxt_key] = new_depth
                queue.append((nxt, new_depth))
            if progress is not None:
                progress.update(1)

    if progress is not None:
        progress.close()
    return heuristic
