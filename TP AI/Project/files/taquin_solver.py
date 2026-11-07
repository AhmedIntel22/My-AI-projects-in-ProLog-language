import time
import copy
from collections import deque

GOAL_STATE = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

INITIAL_STATE = [
    [1, 2, 3],
    [8, 6, 0],
    [7, 5, 4]
]


def state_to_tuple(state):
    return tuple(cell for row in state for cell in row)


def tuple_to_state(t):
    return [[t[r * 3 + c] for c in range(3)] for r in range(3)]


def find_blank(state):
    for r in range(3):
        for c in range(3):
            if state[r][c] == 0:
                return r, c
    raise ValueError("No blank tile found in state.")


def is_goal(state):
    return state == GOAL_STATE


def get_neighbors(state):
    r, c = find_blank(state)
    directions = [(-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right")]
    neighbors = []
    for dr, dc, direction in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_state = copy.deepcopy(state)
            moved_tile = new_state[nr][nc]
            new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
            neighbors.append((new_state, moved_tile, direction))
    return neighbors


def display_state(state, label=""):
    if label:
        print(f"\n{label}")
    print("+---+---+---+")
    for row in state:
        row_str = "| " + " | ".join(str(v) if v != 0 else " " for v in row) + " |"
        print(row_str)
        print("+---+---+---+")


def reconstruct_path(node):
    path = []
    while node is not None:
        path.append(node)
        node = node["parent"]
    path.reverse()
    return path


#========== Heuristics for A* ==========

def misplaced_tiles(state):
    count = 0
    for r in range(3):
        for c in range(3):
            v = state[r][c]
            if v != 0 and v != GOAL_STATE[r][c]:
                count += 1
    return count


def comparison(state):
    goal_pos = {}
    for r in range(3):
        for c in range(3):
            goal_pos[GOAL_STATE[r][c]] = (r, c)
    total = 0
    for r in range(3):
        for c in range(3):
            v = state[r][c]
            if v != 0:
                gr, gc = goal_pos[v]
                total += (r - gr) ** 2 + (c - gc) ** 2
    return total


#========== Algorithm 1 — DFS (Depth-First Search) ==========

def dfs(start, max_nodes=500_000):
    t0 = time.time()
    start_node = {"state": start, "parent": None, "move": None, "tile": None}

    stack = [start_node]                     # freeNodes (LIFO)
    closed = set()
    closed.add(state_to_tuple(start))

    visited_count = 0
    generated_count = 1

    while stack:
        if visited_count > max_nodes:
            return None, visited_count, generated_count, (time.time() - t0) * 1000

        node = stack.pop()
        visited_count += 1

        if is_goal(node["state"]):
            elapsed = (time.time() - t0) * 1000
            return reconstruct_path(node), visited_count, generated_count, elapsed

        for new_state, tile, direction in get_neighbors(node["state"]):
            key = state_to_tuple(new_state)
            if key not in closed:
                closed.add(key)
                generated_count += 1
                child = {"state": new_state, "parent": node,
                         "move": direction, "tile": tile}
                stack.append(child)

    elapsed = (time.time() - t0) * 1000
    return None, visited_count, generated_count, elapsed


#========== Algorithm 2 — BFS (Breadth-First Search) ==========

def bfs(start, max_nodes=500_000):
    t0 = time.time()
    start_node = {"state": start, "parent": None, "move": None, "tile": None}

    queue = deque([start_node])                # freeNodes (FIFO)
    closed = set()
    closed.add(state_to_tuple(start))

    visited_count = 0
    generated_count = 1

    while queue:
        if visited_count > max_nodes:
            return None, visited_count, generated_count, (time.time() - t0) * 1000

        node = queue.popleft()
        visited_count += 1

        if is_goal(node["state"]):
            elapsed = (time.time() - t0) * 1000
            return reconstruct_path(node), visited_count, generated_count, elapsed

        for new_state, tile, direction in get_neighbors(node["state"]):
            key = state_to_tuple(new_state)
            if key not in closed:
                closed.add(key)
                generated_count += 1
                child = {"state": new_state, "parent": node,
                         "move": direction, "tile": tile}
                queue.append(child)

    elapsed = (time.time() - t0) * 1000
    return None, visited_count, generated_count, elapsed


#========== Algorithm 3 — Depth-Limited DFS ==========

def dfs_limited(start, limit):
    visited_count = [0]
    generated_count = [1]

    def _dfs_rec(node, depth, closed):
        visited_count[0] += 1

        if is_goal(node["state"]):
            return reconstruct_path(node)
        if depth == 0:
            return None

        for new_state, tile, direction in get_neighbors(node["state"]):
            key = state_to_tuple(new_state)
            if key not in closed:
                closed.add(key)
                generated_count[0] += 1
                child = {"state": new_state, "parent": node,
                         "move": direction, "tile": tile}
                result = _dfs_rec(child, depth - 1, closed)
                if result is not None:
                    return result
                closed.discard(key)            # backtrack

        return None

    root = {"state": start, "parent": None, "move": None, "tile": None}
    closed = {state_to_tuple(start)}
    path = _dfs_rec(root, limit, closed)
    return path, visited_count[0], generated_count[0]


def dfs_limited_incremental(start, start_l=3):
    t0 = time.time()
    total_visited = 0
    total_generated = 0
    L = start_l

    while L <= 50:
        path, v, g = dfs_limited(start, L)
        total_visited += v
        total_generated += g
        if path is not None:
            elapsed = (time.time() - t0) * 1000
            return path, total_visited, total_generated, elapsed, L
        L += 1

    elapsed = (time.time() - t0) * 1000
    return None, total_visited, total_generated, elapsed, L


#========== Algorithm 4 — A* ==========

def astar(start, max_nodes=500_000):
    import heapq
    t0 = time.time()

    h0 = misplaced_tiles(start) + comparison(start)
    start_node = {"state": start, "parent": None, "move": None,
                  "tile": None, "g": 0, "f": h0}

    counter = 0
    open_heap = [(h0, counter, start_node)]
    open_set = {state_to_tuple(start): 0}    # key → best g so far
    closed = set()

    visited_count = 0
    generated_count = 1

    while open_heap:
        if visited_count > max_nodes:
            return None, visited_count, generated_count, (time.time() - t0) * 1000

        _, _, node = heapq.heappop(open_heap)
        key = state_to_tuple(node["state"])

        if key in closed:
            continue
        closed.add(key)
        visited_count += 1

        if is_goal(node["state"]):
            elapsed = (time.time() - t0) * 1000
            return reconstruct_path(node), visited_count, generated_count, elapsed

        for new_state, tile, direction in get_neighbors(node["state"]):
            nkey = state_to_tuple(new_state)
            if nkey in closed:
                continue
            ng = node["g"] + 1
            if nkey not in open_set or open_set[nkey] > ng:
                open_set[nkey] = ng
                generated_count += 1
                h = misplaced_tiles(new_state) + comparison(new_state)
                child = {"state": new_state, "parent": node,
                         "move": direction, "tile": tile,
                         "g": ng, "f": ng + h}
                counter += 1
                heapq.heappush(open_heap, (ng + h, counter, child))

    elapsed = (time.time() - t0) * 1000
    return None, visited_count, generated_count, elapsed


#========== Result printer ==========
def print_results(algo_name, path, visited, generated, elapsed_ms, extra=""):
    print(f"\n{'='*50}")
    print(f"  {algo_name}{' — ' + extra if extra else ''}")
    print(f"{'='*50}")
    print(f"  Visited nodes   : {visited:,}")
    print(f"  Generated states: {generated:,}")
    print(f"  Execution time  : {elapsed_ms:.2f} ms")
    if path:
        print(f"  Solution length : {len(path) - 1} moves")
        print("\n  Solution path:")
        for i, node in enumerate(path):
            if i == 0:
                display_state(node["state"], f"  Step {i}: Initial state")
            elif i == len(path) - 1:
                display_state(node["state"], f"  Step {i}: Goal state (moved tile {node['tile']} {node['move']})")
            else:
                display_state(node["state"], f"  Step {i}: Move tile {node['tile']} {node['move']}")
    else:
        print("  No solution found.")


#========== Main — run all four algorithms ==========

if __name__ == "__main__":
    print("\n8-Puzzle (Taquin) Solver")
    print("=" * 50)
    display_state(INITIAL_STATE, "Initial state:")
    display_state(GOAL_STATE, "Goal state:")

    path, visited, generated, elapsed = dfs(INITIAL_STATE)
    print_results("DFS — Depth-First Search", path, visited, generated, elapsed)

    path, visited, generated, elapsed = bfs(INITIAL_STATE)
    print_results("BFS — Breadth-First Search", path, visited, generated, elapsed)

    path, visited, generated, elapsed, final_l = dfs_limited_incremental(INITIAL_STATE, start_l=3)
    print_results("Depth-Limited DFS", path, visited, generated, elapsed, extra=f"final L={final_l}")

    path, visited, generated, elapsed = astar(INITIAL_STATE)
    print_results("A* Search", path, visited, generated, elapsed)
