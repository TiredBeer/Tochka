import sys
import collections
import heapq
from dataclasses import dataclass, field


@dataclass(order=True)
class State:
    steps: int
    positions: tuple = field(compare=False)
    keys: frozenset = field(compare=False)


def get_input():
    """Читает лабиринт из stdin в виде списка списков символов."""
    return [list(line.rstrip('\n')) for line in sys.stdin]


def parse_grid(grid):
    n, m = len(grid), len(grid[0])
    starts = []
    key_positions = {}
    for i in range(n):
        for j in range(m):
            c = grid[i][j]
            if c == '@':
                starts.append((i, j))
            elif 'a' <= c <= 'z':
                key_positions[c] = (i, j)

    key_list = sorted(key_positions)
    nodes = starts + [key_positions[k] for k in key_list]
    node_keys = {k: idx + 4 for idx, k in enumerate(key_list)}
    keys = frozenset(key_list)
    return nodes, node_keys, keys


def build_graph(grid, nodes, node_keys):
    n, m = len(grid), len(grid[0])
    graph = [[] for _ in range(len(nodes))]
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for u, (sx, sy) in enumerate(nodes):
        dq = collections.deque([(sx, sy, 0, set())])
        visited = [[False] * m for _ in range(n)]
        visited[sx][sy] = True

        while dq:
            x, y, dist, req = dq.popleft()
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < n and 0 <= ny < m):
                    continue
                if visited[nx][ny] or grid[nx][ny] == '#':
                    continue
                visited[nx][ny] = True

                cell = grid[nx][ny]
                new_req = set(req)
                if 'A' <= cell <= 'Z':
                    new_req.add(cell.lower())

                if 'a' <= cell <= 'z':
                    graph[u].append((
                        cell,
                        node_keys[cell],
                        dist + 1,
                        frozenset(new_req)
                    ))

                dq.append((nx, ny, dist + 1, new_req))
    return graph


def find_min_steps(graph, all_keys):
    number_robots = 4
    start_positions = tuple(range(number_robots))
    start_keys = frozenset()
    heap = [State(0, start_positions, start_keys)]
    best = {(start_positions, start_keys): 0}

    while heap:
        state = heapq.heappop(heap)
        steps, positions, keys = state.steps, state.positions, state.keys

        if best[(positions, keys)] < steps:
            continue
        if keys == all_keys:
            return steps

        for i in range(number_robots):
            u = positions[i]
            for key_char, node_idx, dist, req in graph[u]:
                if key_char in keys or not req.issubset(keys):
                    continue
                new_keys = keys | {key_char}
                next_positions = list(positions)
                next_positions[i] = node_idx
                next_positions = tuple(next_positions)
                new_steps = steps + dist
                key = (next_positions, new_keys)
                if best.get(key, float('inf')) > new_steps:
                    best[key] = new_steps
                    heapq.heappush(heap,
                                   State(new_steps, next_positions, new_keys))
    return -1


def solve(grid):
    nodes, node_keys, all_keys = parse_grid(grid)
    graph = build_graph(grid, nodes, node_keys)
    return find_min_steps(graph, all_keys)


def main():
    grid = get_input()
    print(solve(grid))


if __name__ == '__main__':
    main()
