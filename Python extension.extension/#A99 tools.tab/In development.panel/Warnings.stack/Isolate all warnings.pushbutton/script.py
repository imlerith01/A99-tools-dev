# Dynamo Python node
# IN[0]: n_data_rows (int)        default 6
# IN[1]: n_cols (int)             default 20
# IN[2]: seed (int/None)          optional
# IN[3]: values (list)            default ['a','b','c']
# IN[4]: fill_x (bool)            default True
# IN[5]: target_ratios [a,b,c]    default [0.5, 0.25, 0.25]

import random
import math

# ---------- Inputs ----------
def _get(i, default=None):
    return IN[i] if len(IN) > i else default

n_data_rows = int(_get(0, 6) or 6)
n_cols      = int(_get(1, 20) or 20)
seed        = _get(2, None)
vals        = _get(3, ['a','b','c']) or ['a','b','c']
fill_x      = bool(_get(4, True))
ratios_in   = _get(5, [0.5, 0.25, 0.25]) or [0.5, 0.25, 0.25]

if seed is not None:
    try: random.seed(seed)
    except: pass

# symbols
base = ['a','b','c']
if len(vals) < 3:
    vals = (vals + base)[:3]
else:
    vals = vals[:3]
A, B, C = vals[0], vals[1], vals[2]

# ratios sanity + normalize
if not isinstance(ratios_in, list) or len(ratios_in) < 3:
    ratios_in = [0.5, 0.25, 0.25]
ra, rb, rc = ratios_in[:3]
s = float(ra + rb + rc)
if s <= 0: ra, rb, rc = 0.5, 0.25, 0.25
else:       ra, rb, rc = ra/s, rb/s, rc/s

total_data_cells = n_data_rows * n_cols

# Target counts for DATA rows only
base_counts = [math.floor(ra*total_data_cells),
               math.floor(rb*total_data_cells),
               math.floor(rc*total_data_cells)]
assigned = sum(base_counts)
remainder = total_data_cells - assigned
fracs = [(ra - base_counts[0]/float(total_data_cells), 0),
         (rb - base_counts[1]/float(total_data_cells), 1),
         (rc - base_counts[2]/float(total_data_cells), 2)]
fracs.sort(reverse=True)
i = 0
while remainder > 0:
    base_counts[fracs[i % 3][1]] += 1
    remainder -= 1
    i += 1
target_counts = {A: base_counts[0], B: base_counts[1], C: base_counts[2]}
used_counts   = {A: 0, B: 0, C: 0}

def remaining(symbol):
    return target_counts[symbol] - used_counts[symbol]

# ---------- Helpers ----------
def allowed_below(above, options):
    """Block B↕C adjacency on data rows."""
    if above == B:
        return [x for x in options if x != C]
    if above == C:
        return [x for x in options if x != B]
    return list(options)

def pick_by_quota(options):
    """Sample from options with probability proportional to remaining quota."""
    if not options:
        return A
    rems = [max(0, remaining(o)) for o in options]
    tot = sum(rems)
    if tot <= 0:
        return random.choice(options)
    r = random.random() * tot
    acc = 0.0
    for o, w in zip(options, rems):
        acc += w
        if r <= acc:
            return o
    return options[-1]

def different_from(x):
    return [s for s in (A,B,C) if s != x]

def per_row_counts(n_cols, ra, rb, rc):
    """Compute per-row counts for a/b/c that match ratios (sum to n_cols)."""
    base = [math.floor(ra*n_cols), math.floor(rb*n_cols), math.floor(rc*n_cols)]
    assigned = sum(base)
    rem = n_cols - assigned
    fr = [(ra - base[0]/float(n_cols), 0),
          (rb - base[1]/float(n_cols), 1),
          (rc - base[2]/float(n_cols), 2)]
    fr.sort(reverse=True)
    i = 0
    while rem > 0:
        base[fr[i % 3][1]] += 1
        rem -= 1
        i += 1
    return {A: base[0], B: base[1], C: base[2]}

# ---------- Build DATA rows (quota-aware) ----------
data = [[None]*n_cols for _ in range(n_data_rows)]

# Row 1: enforce 50/25/25 on this row, then shuffle (prevents all 'a')
row1_target = per_row_counts(n_cols, ra, rb, rc)  # e.g., {A:10,B:5,C:5} for 20 cols
row1_list = [A]*row1_target[A] + [B]*row1_target[B] + [C]*row1_target[C]
random.shuffle(row1_list)
data[0] = row1_list
for v in data[0]:
    used_counts[v] += 1

# Row 2: exactly 50% match Row 1; others differ (quota-aware + adjacency)
idxs = list(range(n_cols))
random.shuffle(idxs)
match_count = n_cols // 2
match_idxs = set(idxs[:match_count])

row2 = [None]*n_cols
for j in range(n_cols):
    above = data[0][j]
    if j in match_idxs:
        row2[j] = above
        used_counts[above] += 1
    else:
        options = different_from(above)
        options = allowed_below(above, options)
        choice = pick_by_quota(options)
        row2[j] = choice
        used_counts[choice] += 1
data[1] = row2

# Rows 3..: two-row rule + adjacency, pick by quota when we have a choice
for i in range(2, n_data_rows):
    row = [None]*n_cols
    for j in range(n_cols):
        above2 = data[i-1][j]  # nearer
        above1 = data[i-2][j]  # farther
        if above1 == above2:
            options = different_from(above2)
            options = allowed_below(above2, options)
            choice = pick_by_quota(options)
            row[j] = choice
            used_counts[choice] += 1
        else:
            choice = above2
            row[j] = choice
            used_counts[choice] += 1
    data[i] = row

# ---------- Interleave calculated rows ----------
final_table = []
for i in range(n_data_rows):
    final_table.append(list(data[i]))
    calc = [None]*n_cols
    if i < n_data_rows - 1:
        above_row = data[i]
        below_row = data[i+1]
        for j in range(n_cols):
            calc[j] = above_row[j] if above_row[j] == below_row[j] else None
    final_table.append(calc)

# ---------- Fill empty with x ----------
if fill_x:
    for i in range(len(final_table)):
        for j in range(n_cols):
            if final_table[i][j] is None or final_table[i][j] == '':
                final_table[i][j] = 'x'

# ---------- Remove trailing x-only row ----------
if final_table and all(cell == 'x' for cell in final_table[-1]):
    final_table.pop()

# ---------- Stats (ignoring x) ----------
achieved_counts_no_x = {A:0, B:0, C:0}
for row in final_table:
    for v in row:
        if v in achieved_counts_no_x:   # skip 'x'
            achieved_counts_no_x[v] += 1

total_non_x = float(sum(achieved_counts_no_x.values())) or 1.0
proportions_no_x = {
    A: achieved_counts_no_x[A]/total_non_x,
    B: achieved_counts_no_x[B]/total_non_x,
    C: achieved_counts_no_x[C]/total_non_x
}

OUT = [final_table, {
    "target_counts_data": target_counts,
    "achieved_counts_ignoring_x": achieved_counts_no_x,
    "proportions_ignoring_x": proportions_no_x
}]
