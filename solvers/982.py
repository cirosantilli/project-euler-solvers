import math
from itertools import product

EPS = 1e-9


def pivot(tableau, basis, row, col):
    pivot_val = tableau[row][col]
    inv = 1.0 / pivot_val
    n_cols = len(tableau[0])
    # Normalize pivot row
    for j in range(n_cols):
        tableau[row][j] *= inv
    # Eliminate column in other rows
    for i in range(len(tableau)):
        if i == row:
            continue
        factor = tableau[i][col]
        if abs(factor) > EPS:
            for j in range(n_cols):
                tableau[i][j] -= factor * tableau[row][j]
    basis[row] = col


def set_objective(tableau, basis, c):
    m = len(basis)
    n = len(tableau[0]) - 1
    obj = [-c[j] for j in range(n)] + [0.0]
    for i in range(m):
        cb = c[basis[i]]
        if abs(cb) > EPS:
            row = tableau[i]
            for j in range(n + 1):
                obj[j] += cb * row[j]
    if len(tableau) == m:
        tableau.append(obj)
    else:
        tableau[m] = obj


def simplex_max(tableau, basis):
    m = len(basis)
    n = len(tableau[0]) - 1
    max_iter = 200000
    for _ in range(max_iter):
        # Choose entering variable (most negative reduced cost)
        entering = None
        for j in range(n):
            if tableau[m][j] < -EPS:
                entering = j
                break
        if entering is None:
            return True
        # Choose leaving variable by minimum ratio test
        min_ratio = float("inf")
        leaving = None
        for i in range(m):
            a = tableau[i][entering]
            if a > EPS:
                ratio = tableau[i][-1] / a
                if ratio < min_ratio - EPS:
                    min_ratio = ratio
                    leaving = i
        if leaving is None:
            return False
        pivot(tableau, basis, leaving, entering)
    raise RuntimeError("Simplex did not converge")


def build_tableau(n_vars, constraints):
    rows = []
    rhs = []
    basis = []
    art_indices = []
    n_total = n_vars

    def add_var():
        nonlocal n_total
        for r in rows:
            r.append(0.0)
        n_total += 1

    for coeffs, sense, b in constraints:
        if b < 0:
            coeffs = [-v for v in coeffs]
            b = -b
            if sense == "<=":
                sense = ">="
            elif sense == ">=":
                sense = "<="
        row = list(coeffs) + [0.0] * (n_total - n_vars)
        if sense == "<=":
            add_var()
            row.append(1.0)
            basis.append(n_total - 1)
        elif sense == ">=":
            add_var()
            row.append(-1.0)
            add_var()
            row.append(1.0)
            basis.append(n_total - 1)
            art_indices.append(n_total - 1)
        elif sense == "=":
            add_var()
            row.append(1.0)
            basis.append(n_total - 1)
            art_indices.append(n_total - 1)
        else:
            raise ValueError("Unknown constraint sense")
        rows.append(row)
        rhs.append(b)

    tableau = [rows[i] + [rhs[i]] for i in range(len(rows))]
    return tableau, basis, art_indices, n_total


def remove_artificial(tableau, basis, art_indices):
    art_set = set(art_indices)
    m = len(basis)
    n = len(tableau[0]) - 1
    i = 0
    while i < m:
        if basis[i] in art_set:
            pivot_col = None
            for j in range(n):
                if j in art_set:
                    continue
                if abs(tableau[i][j]) > EPS:
                    pivot_col = j
                    break
            if pivot_col is not None:
                pivot(tableau, basis, i, pivot_col)
                i += 1
            else:
                if abs(tableau[i][-1]) > EPS:
                    raise RuntimeError("Infeasible during artificial removal")
                tableau.pop(i)
                basis.pop(i)
                m -= 1
                continue
        else:
            i += 1
    n = len(tableau[0]) - 1
    keep_cols = [j for j in range(n) if j not in art_set]
    mapping = {old: new for new, old in enumerate(keep_cols)}
    new_tableau = []
    for row in tableau:
        new_row = [row[j] for j in keep_cols] + [row[-1]]
        new_tableau.append(new_row)
    new_basis = [mapping[b] for b in basis]
    return new_tableau, new_basis, mapping


def solve_lp(n_vars, constraints, objective):
    tableau, basis, art_indices, n_total = build_tableau(n_vars, constraints)

    # Phase I: maximize -sum(artificial)
    if art_indices:
        c_phase1 = [0.0] * n_total
        for j in art_indices:
            c_phase1[j] = -1.0
        set_objective(tableau, basis, c_phase1)
        if not simplex_max(tableau, basis):
            raise RuntimeError("Unbounded in phase I")
        if tableau[-1][-1] < -1e-7:
            raise RuntimeError("Infeasible LP")
        tableau.pop()  # remove objective row
        tableau, basis, mapping = remove_artificial(tableau, basis, art_indices)
    else:
        mapping = {i: i for i in range(n_total)}

    n_total2 = len(tableau[0]) - 1
    c_phase2 = [0.0] * n_total2
    for j, coef in enumerate(objective):
        if j in mapping:
            c_phase2[mapping[j]] = -coef
    set_objective(tableau, basis, c_phase2)
    if not simplex_max(tableau, basis):
        raise RuntimeError("Unbounded in phase II")
    # Minimum value is negative of maximized value
    return -tableau[-1][-1]


def build_and_solve(num_dice):
    values = [1, 2, 3, 4, 5, 6]
    states = list(product(values, repeat=num_dice))
    num_states = len(states)
    hide_options = list(range(num_dice))

    # Signals are sorted tuples of revealed values
    signal_set = set()
    for t in states:
        for h in hide_options:
            revealed = [t[i] for i in range(num_dice) if i != h]
            signal_set.add(tuple(sorted(revealed)))
    signals = sorted(signal_set)
    signal_index = {s: i for i, s in enumerate(signals)}

    num_x = num_states * num_dice
    num_z = len(signals)
    n_vars = num_x + num_z

    def x_index(state_idx, hide_idx):
        return state_idx * num_dice + hide_idx

    def z_index(signal_idx):
        return num_x + signal_idx

    constraints = []
    p_state = 1.0 / num_states

    # For each state: sum_h x[t,h] = p_state
    for s_idx in range(num_states):
        coeffs = [0.0] * n_vars
        for h in hide_options:
            coeffs[x_index(s_idx, h)] = 1.0
        constraints.append((coeffs, "=", p_state))

    # For each signal: -z + b*P <= 0 and -z + H <= 0
    for sig in signals:
        b_val = max(sig)
        sig_idx = signal_index[sig]

        coeffs_vis = [0.0] * n_vars
        coeffs_hid = [0.0] * n_vars
        coeffs_vis[z_index(sig_idx)] = -1.0
        coeffs_hid[z_index(sig_idx)] = -1.0

        for s_idx, t in enumerate(states):
            for h in hide_options:
                revealed = [t[i] for i in range(num_dice) if i != h]
                if tuple(sorted(revealed)) == sig:
                    coeffs_vis[x_index(s_idx, h)] += b_val
                    hidden_val = t[h]
                    coeffs_hid[x_index(s_idx, h)] += hidden_val

        constraints.append((coeffs_vis, "<=", 0.0))
        constraints.append((coeffs_hid, "<=", 0.0))

    # Objective: minimize sum z
    objective = [0.0] * n_vars
    for sig_idx in range(num_z):
        objective[z_index(sig_idx)] = 1.0

    return solve_lp(n_vars, constraints, objective)


def main():
    # Validate the two-dice game value from the problem statement
    val_two = build_and_solve(2)
    target_exact = 145.0 / 36.0
    assert abs(val_two - target_exact) < 1e-8
    assert abs(val_two - 4.027778) < 1e-6

    val_three = build_and_solve(3)
    print(f"{val_three:.6f}")


if __name__ == "__main__":
    main()
