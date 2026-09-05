##################
# Minesweeperdle #
##################

from itertools import combinations
from math import factorial
import time

GRID = """
------
-5---3
3--3--
----5-
-4----
1--1--
"""
MINES = 16

GRID = """
-5-4-
-----
4--6-
-----
---3-
"""
MINES = 12

#####

DRCS = ((-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1))

grid = GRID.split('\n')[1:-1]
ROWS = len(grid)
COLS = len(grid[0])
SIZE = ROWS*COLS
MASKS = tuple(1 << rc for rc in range(SIZE))
ALL_ONES = (1 << SIZE) - 1

for row in grid:
    if len(grid) != COLS:
        raise Exception("Row of different length.")
grid = [grid[r][c] for r in range(ROWS) for c in range(COLS)]
grid = [-1 if x == '-' else int(x) for x in grid]

#####

def print_grid(grid):
    rows = [[' ', '  '] + [' '+str(c+1) for c in range(COLS)], []]
    for r in range(ROWS):
        row = [chr(ord('A')+r), '  ']
        for c in range(COLS):
            i = r * ROWS + c
            match grid[i]:
                case -1:
                    row.append(' -')
                case -2:
                    row.append(' X')
                case -3:
                    row.append(' ?')
                case _:
                    row.append(' ' + str(grid[i]))
        rows.append(row)
    print()
    for row in rows:
        print(''.join(row))

def neighbours_of(i):
    r = i // ROWS
    c = i % ROWS
    nbs = []
    for dr, dc in DRCS:
        nr = r + dr
        if not 0 <= nr < ROWS:
            continue
        nc = c + dc
        if not 0 <= nc < COLS:
            continue
        nbs.append(nr*ROWS + nc)
    return nbs

def num_to_masks(i, num_mines):
    nbs = neighbours_of(i)
    num_cells = len(nbs)
    if num_mines > num_cells:
        raise Exception("Not enough cells ({num} > {len(nbs)}) around {i}.")
    masks = []
    perms = combinations(range(num_cells), num_mines)
    for perm in perms:
        mineness = [False for _ in range(num_cells)]
        for j in perm:
            mineness[j] = True
        mine_mask = 0
        safe_mask = MASKS[i]
        for j in range(num_cells):
            if mineness[j]:
                mine_mask |= MASKS[nbs[j]]
            else:
                safe_mask |= MASKS[nbs[j]]
        masks.append((mine_mask, safe_mask))
    return masks

def update(i, states):
    masks = num_to_masks(i, grid[i])
    new_states = []
    for state in states:
        for mine_mask, safe_mask in masks:
            if state & mine_mask:
                continue
            if state & safe_mask == safe_mask:
                new_states.append(state)
                break
    return new_states

def mine_count(state):
    return sum(bool(state ^ MASKS[i]) for i in range(SIZE))

def check_mine_count(states):
    return tuple(state for state in states if mine_count(state) == MINES)
        
def merge(states):
    mine_mask = 0
    safe_mask = ALL_ONES
    for state in states:
        mine_mask |= state
        safe_mask &= state
    mines = []
    safes = []
    for i in range(SIZE):
        mask = MASKS[i]
        if not mine_mask & mask:
            mines.append(i)
        if safe_mask & mask:
            safes.append(i)
    return (mines, safes)

#####

first_tiles = set()
other_tiles = []
for i in range(SIZE):
    if grid[i] == -1:
        other_tiles.append(i)
    else:
        first_tiles.add(i)

num_grids = factorial(len(other_tiles))
num_grids //= factorial(MINES) * factorial(len(other_tiles)-MINES)

print(f"Generating {len(other_tiles)}C{MINES} = {num_grids:,} grids...")
states = []
start = time.time()
for perm in combinations(other_tiles, MINES):
    state = ALL_ONES
    for i in perm:
        state ^= MASKS[i]
    states.append(state)
print(f"Took {time.time()-start:.2f} s\n")

print(f"Filtering grids...")
start = time.time()
for i in range(SIZE):
    if grid[i] == -1:
        continue
    states = update(i, states)
print(f"Took {time.time()-start:.2f} s\n")


print(f"Merging grids...")
mines, safes = merge(states)
for i in mines:
    grid[i] = -2

new_tiles = []
for i in safes:
    if i not in first_tiles:
        grid[i] = -3
        first_tiles.add(i)
        new_tiles.append(i)

while new_tiles:
    print_grid(grid)
    for i in new_tiles:
        cell = chr(ord('A') + i//ROWS) + str(i%ROWS + 1)
        x = input(f"\n{cell} is safe. Value: ")
        # pray user doesn't make a mistake
        grid[i] = int(x)
        states = update(i, states)
        print(f"Set {cell} to {grid[i]}")

    mines, safes = merge(states)
    for i in mines:
        grid[i] = -2
    new_tiles = []
    for i in safes:
        if i not in first_tiles:
            grid[i] = -3
            first_tiles.add(i)
            new_tiles.append(i)

if len(states) == 1:
    print("\nDone!")
    print_grid(grid)
else:
    print("\nSomething went wrong :(")
