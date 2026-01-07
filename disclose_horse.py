#################
# enclose.horse #
#################

from itertools import combinations
import time

# Inputs

BOARD = """
001100010000
041411111110
114111111011
141400110010
010100111110
011111111110
111101001110
011100h01111
011111111111
011111001110
110011004140
010111111410
011111114140
010010101110
"""

WALLS = 12
SEED = (#(0, 3), (0, 7),
        (1, 2),
        (2, 3), (2, 11),
        (5, 3),
        (7, 11),
        (8, 5), (8, 11),
        (11, 8),
        (12, 9),
        (13, 10))


# Processing

if len(SEED) > WALLS:
    raise ValueError(f"Too many walls: {len(SEED)} > {WALLS}.")

board = [list(row) for row in BOARD.split('\n') if row]
rows, cols = len(board), len(board[0])

for x, y in SEED:
    if board[x][y] != '1':
        raise ValueError(f"{(x, y)} in SEED is not on a grass tile.")
    board[x][y] = '|'
board = tuple(''.join(row) for row in board)

grid = []
wallable = []
horse = ()
for r in range(rows):
    if cols != len(board[r]):
        raise ValueError(f"Row {r} has {len(board[r])} != {cols} tiles.")
    new_row = []
    for c in range(cols):
        char = board[r][c]
        if char == '1':
            wallable.append((r, c))
        if char == '|':
            char = '0'
        elif char == 'h':
            if horse:
                raise ValueError("Another horse found at {(r, c)}.")
            horse = (r, c)
            char = '1'
        new_row.append(int(char))
    grid.append(tuple(new_row))

if not horse:
    raise ValueError("No horse 'h' found.")

grid = tuple(tuple(row for row in grid))
wallable = tuple(wallable)


# Printing Input

print("Seed")
for row in board:
    to_print = []
    for c in row:
        match c:
            case '0':
                c = 'X'
            case '1':
                c = '-'
            case '4':
                c = 'C'
        to_print.append(c)
    print("  " + ' '.join(to_print))
print()


# Brute-forcing

def try_flood(walls):
    test = [list(row) for row in grid]
    for x, y in walls:
        test[x][y] = 0
    score = 0
    NBS = ((0, 1), (0, -1), (1, 0), (-1, 0))
    def flood(x, y):
        nonlocal score
        score += test[x][y]
        test[x][y] = 0
        for dx, dy in NBS:
            x2, y2 = x + dx, y + dy
            if not (0 <= x2 < rows and 0 <= y2 < cols):
                raise ValueError()
            if test[x2][y2]:
                flood(x2, y2)
    try:
        flood(*horse)
    except ValueError:
        score = 0
    return score

best_score, best_walls = 0, ()
start, count, checkpoint = time.time(), 0, 1
for walls in combinations(wallable, WALLS - len(SEED)):
    score = try_flood(walls)
    if score > best_score:
        best_score = score
        best_walls = walls
        print(f"  New high score: {best_score}")
    count += 1
    if count == 10 ** checkpoint:
        dur = round(time.time() - start)
        print(f"At 1e{checkpoint} combinations in {dur}s.")
        checkpoint += 1


# Printing Output

board = [list(row) for row in board]
for x, y in best_walls:
    board[x][y] = '|'

print(f"\nOptimal: {best_score}")
for row in board:
    to_print = []
    for c in row:
        match c:
            case '0':
                c = 'X'
            case '1':
                c = ' '
            case '4':
                c = 'C'
        to_print.append(c)
    print("  " + ' '.join(to_print))
