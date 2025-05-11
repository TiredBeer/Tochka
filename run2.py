import sys
from collections import deque, defaultdict
import heapq
from typing import NamedTuple

# Использование dataclass/NamedTuple замедляет выполнение кода
Position = tuple[int, int]


class ParsedGrid(NamedTuple):
    start_positions: list[Position]
    key_positions: dict[str, Position]


class PriorityQueueEntry(NamedTuple):
    priority: int
    cost: int
    state: tuple[int, ...]

    def __lt__(self, other: "PriorityQueueEntry") -> bool:
        return self.priority < other.priority


def get_input() -> list[list[str]]:
    """
    Читает входной лабиринт из стандартного ввода и возвращает список списков символов.
    """
    return [list(line.strip("\n")) for line in sys.stdin]


def parse_grid(grid: list[list[str]]) -> ParsedGrid:
    """
    Находит стартовые позиции роботов и позиции ключей в сетке.
    Возвращает ParsedGrid: start_positions и key_positions.
    """
    start_positions: list[Position] = []
    key_positions: dict[str, Position] = {}
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == '@':
                start_positions.append((r, c))
            elif 'a' <= cell <= 'z':
                key_positions[cell] = (r, c)
    return ParsedGrid(start_positions, key_positions)


def index_points(
        start_positions: list[Position],
        key_positions: dict[str, Position]
) -> tuple[list[Position], dict[Position, int]]:
    """
    Строит список точек интереса: сначала старты, затем ключи в лексикографическом порядке.
    Возвращает all_points и маппинг coordinate_to_index.
    """
    sorted_keys = sorted(key_positions)
    all_points: list[Position] = [*start_positions] + [key_positions[k] for k in
                                                       sorted_keys]
    coordinate_to_index = {pt: idx for idx, pt in enumerate(all_points)}
    return all_points, coordinate_to_index


def build_reachability_graph(
        grid: list[list[str]],
        points: list[Position],
        coordinate_to_index: dict[Position, int]
) -> list[dict[int, list[tuple[int, int]]]]:
    """
    Для каждой точки рассчитывает все достижимые другие точки вместе с маской дверей и расстоянием.
    Возвращает список словарей: graph[source_index][target_index] = [(door_mask, distance), ...].
    """
    number_of_points = len(points)
    num_rows, num_cols = len(grid), len(grid[0])
    graph = [defaultdict(list) for _ in range(number_of_points)]

    for source_index, (start_row, start_col) in enumerate(points):
        visited_masks = {(start_row, start_col): [0]}
        bfs_queue = deque(
            [(start_row, start_col, 0, 0)])

        while bfs_queue:
            row, col, distance, door_mask = bfs_queue.popleft()
            target_index = coordinate_to_index.get((row, col))
            if target_index is not None and target_index != source_index:
                graph[source_index][target_index].append((door_mask, distance))

            for d_row, d_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                new_row, new_col = row + d_row, col + d_col
                if not (0 <= new_row < num_rows and 0 <= new_col < num_cols):
                    continue
                cell_value = grid[new_row][new_col]
                if cell_value == '#':
                    continue

                new_distance = distance + 1
                new_door_mask = door_mask
                if 'A' <= cell_value <= 'Z':
                    door_key_index = ord(cell_value.lower()) - ord('a')
                    new_door_mask |= (1 << door_key_index)

                previous_masks = visited_masks.get((new_row, new_col))
                if previous_masks:

                    if any((old_mask & new_door_mask) == old_mask for old_mask
                           in previous_masks):
                        continue

                    visited_masks[(new_row, new_col)] = [
                        mask for mask in previous_masks
                        if not ((new_door_mask & mask) == new_door_mask)]
                    visited_masks[(new_row, new_col)].append(new_door_mask)
                else:
                    visited_masks[(new_row, new_col)] = [new_door_mask]

                bfs_queue.append(
                    (new_row, new_col, new_distance, new_door_mask))

    return graph


def apply_pareto_filter(
        graph: list[dict[int, list[tuple[int, int]]]]) -> None:
    """
    Оставляет в каждой ячейке graph[source][target] только недоминируемые варианты (по двери и расстоянию).
    """
    for source_index in range(len(graph)):
        for target_index, variants in list(graph[source_index].items()):
            best_distances = {}
            for mask, distance in variants:
                if (mask not in best_distances
                        or distance < best_distances[mask]):
                    best_distances[mask] = distance

            filtered = []
            for mask, distance in best_distances.items():
                is_dominated = any(
                    other_mask != mask and
                    (other_mask & mask) == other_mask and
                    best_distances[other_mask] <= distance
                    for other_mask in best_distances
                )
                if not is_dominated:
                    filtered.append((mask, distance))

            graph[source_index][target_index] = filtered


def compute_minimum_edge_length(
        graph: list[dict[int, list[tuple[int, int]]]]) -> int:
    """
    Находит минимальное расстояние среди всех ребер графа, нужен для эвристики A*.
    """
    all_distances = [distance for adj in graph for variants in adj.values() for
                     (mask, distance) in variants]
    return min(all_distances) if all_distances else 0


def a_star_search(
        graph: list[dict[int, list[tuple[int, int]]]],
        num_keys: int
) -> int:
    """
    Выполняет A*-поиск по состояниям роботов и собранных ключей.
    Возвращает минимальное число шагов или -1, если сбор всех ключей невозможен.
    """
    number_of_points = len(graph)
    all_keys_collected = (1 << num_keys) - 1
    start_state = (0, 1, 2, 3, 0)
    min_edge_length = compute_minimum_edge_length(graph)

    def heuristic(state):
        collected_mask = state[4]
        collected_count = bin(collected_mask).count('1')
        remaining_keys = num_keys - collected_count
        return remaining_keys * min_edge_length

    priority_queue = []
    heapq.heappush(
        priority_queue,
        PriorityQueueEntry(
            priority=heuristic(start_state),
            cost=0,
            state=start_state
        )
    )
    best_cost = {start_state: 0}

    while priority_queue:
        entry = heapq.heappop(priority_queue)
        current_cost, current_state = entry.cost, entry.state
        if current_cost > best_cost.get(current_state, float('inf')):
            continue
        if current_state[4] == all_keys_collected:
            return current_cost

        robot_positions, keys_mask = current_state[:4], current_state[4]
        for robot_index, robot_point in enumerate(robot_positions):
            for target_point in range(4, number_of_points):
                key_bit = 1 << (target_point - 4)
                if keys_mask & key_bit:
                    continue
                for required_mask, distance in graph[robot_point].get(
                        target_point, []):
                    if required_mask & ~keys_mask:
                        continue

                    new_keys_mask = keys_mask | key_bit
                    new_positions = list(robot_positions)
                    new_positions[robot_index] = target_point
                    new_state = (*new_positions, new_keys_mask)
                    tentative_cost = current_cost + distance
                    if tentative_cost < best_cost.get(new_state, float('inf')):
                        best_cost[new_state] = tentative_cost
                        heapq.heappush(
                            priority_queue,
                            PriorityQueueEntry(
                                priority=tentative_cost + heuristic(new_state),
                                cost=tentative_cost,
                                state=new_state
                            )
                        )
    return -1


def solve(grid: list[list[str]]) -> int:
    """
    Координирует разбор сетки, построение графа и запуск A*-поиска.
    """
    parsed = parse_grid(grid)
    start_positions, key_positions = parsed.start_positions, parsed.key_positions
    points, coordinate_to_index = index_points(start_positions, key_positions)
    graph = build_reachability_graph(grid, points, coordinate_to_index)
    apply_pareto_filter(graph)
    return a_star_search(graph, len(key_positions))


def main():
    data = get_input()
    result = solve(data)
    print(result)


if __name__ == '__main__':
    main()