import sys
import collections
import heapq
from dataclasses import dataclass, field


@dataclass(order=True)
class State:
    steps: int
    positions: tuple = field(compare=False)
    mask: int = field(compare=False)


def get_input():
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
    nodes = starts + [key_positions[c] for c in key_list]
    key_idx = {c: i for i, c in enumerate(key_list)}
    key_node = {c: i + 4 for i, c in enumerate(key_list)}
    keys_mask = (1 << len(key_list)) - 1
    return nodes, key_idx, key_node, keys_mask


def build_graph(grid, nodes, key_idx, key_node):
    n, m = len(grid), len(grid[0])
    graph = [[] for _ in nodes]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for u, (sx, sy) in enumerate(nodes):
        dq = collections.deque([(sx, sy, 0, 0)])
        visited_states = {(sx, sy, 0)}

        while dq:
            x, y, dist, req = dq.popleft()
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < n and 0 <= ny < m):
                    continue
                cell = grid[nx][ny]
                if cell == '#':
                    continue

                req2 = req
                if 'A' <= cell <= 'Z':
                    k = cell.lower()
                    if k in key_idx:
                        req2 |= 1 << key_idx[k]

                state = (nx, ny, req2)
                if state in visited_states:
                    continue
                visited_states.add(state)

                if 'a' <= cell <= 'z':
                    graph[u].append((
                        key_node[cell],
                        dist + 1,
                        req2
                    ))
                dq.append((nx, ny, dist + 1, req2))
    return graph


def find_min_steps(graph, keys_mask):
    num_robots = 4
    start_positions = tuple(range(num_robots))
    start_mask = 0

    heap = [State(0, start_positions, start_mask)]
    best = {(start_positions, start_mask): 0}

    while heap:
        st = heapq.heappop(heap)
        steps, poses, mask = st.steps, st.positions, st.mask
        if best[(poses, mask)] < steps:
            continue
        if mask == keys_mask:
            return steps

        for i in range(num_robots):
            u = poses[i]
            for node_idx, dist, req_mask in graph[u]:
                key_bit = 1 << (node_idx - 4)
                if mask & key_bit:
                    continue
                if req_mask & ~mask:
                    continue

                new_mask = mask | key_bit
                new_poses = list(poses)
                new_poses[i] = node_idx
                new_poses = tuple(new_poses)
                new_steps = steps + dist
                state = (new_poses, new_mask)
                if best.get(state, float('inf')) > new_steps:
                    best[state] = new_steps
                    heapq.heappush(
                        heap,
                        State(new_steps, new_poses, new_mask)
                    )
    return -1


def solve(grid):
    nodes, key_idx, key_node, keys_mask = parse_grid(grid)
    graph = build_graph(grid, nodes, key_idx, key_node)
    return find_min_steps(graph, keys_mask)


def main():
    grid = get_input()
    print(solve(grid))


if __name__ == '__main__':
    main()
