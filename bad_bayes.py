COLS = 4
ROWS = 5

MASKS = tuple((cr, 1 << cr) for cr in range(COLS * ROWS))
EDGES = tuple([(c, 0) for c in range(COLS)] +
              [(0, r) for r in range(1, ROWS - 1)] +
              [(COLS - 1, r) for r in range(1, ROWS - 1)] +
              [(c, ROWS - 1) for c in range(COLS)])

for r in range(ROWS):
    for c in range(COLS):
        exec(f"{chr(ord('a') + c)}{r + 1} = {(c, r)}")
        exec(f"{chr(ord('A') + c)}{r + 1} = {(c, r)}")
    

for r in range(ROWS):
    row = tuple((c, r) for c in range(COLS))
    exec(f"row_{r + 1} = {row}")

for c in range(COLS):
    col = tuple((c, r) for r in range(ROWS))
    exec(f"col_{chr(ord('a') + c)} = {col}")
    exec(f"col_{chr(ord('A') + c)} = {col}")

states = range(1 << COLS * ROWS)
old_states = states

ALL_ONE = (1 << (COLS * ROWS)) - 1
def update():
    i_board = ALL_ONE
    c_board = ALL_ONE
    for state in states:
        i_board &= state
        c_board &= ~state
    
    state = ['-'] * (COLS * ROWS)
    for i, mask in MASKS:
        if mask & i_board:
            state[i] = 'I'
        if mask & c_board:
            state[i] = 'C'

    for r in range(ROWS):
        print(' '.join(state[r * COLS : (r + 1) * COLS]))
    print(f"{len(states)} states.\n")

def make_mask(cells):
    mask = 0
    for c, r in cells:
        cr = r * COLS + c
        mask |= MASKS[cr][1]
    return mask


# bools

def is_innocent(state, *cells):
    mask = make_mask(cells)
    return mask & state == mask

def is_criminal(state, *cells):
    mask = make_mask(cells)
    return mask & ~state == mask


# lists

def above(cell):
    c, r = cell
    return [(c, r2) for r2 in range(r)]

def below(cell):
    c, r = cell
    return [(c, r2) for r2 in range(r + 1, ROWS)]

NBS = ((-1,  1), (0,  1), (1,  1),
       (-1,  0),          (1,  0),
       (-1, -1), (0, -1), (1, -1))
def neighbours(cell):
    c, r = cell
    return [(c + nb[0], r + nb[1]) for nb in NBS
            if 0 <= c + nb[0] < COLS and 0 <= r + nb[1] < ROWS]
nbs = neighbours

def overlap(*cellss):
    oomfs = cellss[0]
    for cells in cellss[1:]:
        oomfs = [cell for cell in cells if cell in oomfs]
    return oomfs

def mutuals(*cells):
    return overlap(*(neighbours(cell) for cell in cells))

def innocents_from(state, cells):
    return [cell for cell in cells if is_innocent(state, cell)]

def criminals_from(state, cells):
    return [cell for cell in cells if not is_innocent(state, cell)]

def num_innocents(state, cells):
    return len(innocents_from(state, cells))

def num_criminals(state, cells):
    return len(criminals_from(state, cells))


# interface

def add_clue(clue):
    global old_states, states
    old_states = states
    states = tuple(filter(clue, states))
    update()

clue = lambda state: True
def use():
    add_clue(clue)

def undo():
    # works as redo too
    global states, old_states
    states, old_states = old_states, states
    update()

def set_innocent(*cells):
    mask = make_mask(cells)
    add_clue(lambda s: s & mask == mask)
inno = set_innocent

def set_criminal(*cells):
    mask = make_mask(cells)
    add_clue(lambda s: ~s & mask == mask)
crim = set_criminal

def has_innocents(cells, n):
    add_clue(lambda s: num_innocents(s, cells) == n)

def has_criminals(cells, n):
    add_clue(lambda s: num_criminals(s, cells) == n)
