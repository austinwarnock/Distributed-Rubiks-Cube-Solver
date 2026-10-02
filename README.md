# Distributed-Rubics-Cube-Solver

## Terminal visualizer

```bash
python3 visualize.py                    # solved cube (ANSI colors)
python3 visualize.py --scramble 15    # random scramble
python3 visualize.py -m "R U R' U'" --step
python3 visualize.py --interactive      # type moves at a prompt
```

Cube turns use precomputed 54-sticker permutation tables (`move_permutations.py`) for fast in-place transforms.
