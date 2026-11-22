from collections import deque
import heapq


def breadth_first_search(graph, start):
    """Visit nodes in breadth-first order."""
    visited = set([start])
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return order


def depth_first_search(graph, start):
    """Visit nodes in depth-first order."""
    visited = set()
    order = []

    def visit(node):
        visited.add(node)
        order.append(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                visit(neighbour)

    visit(start)
    return order


def dijkstra(graph, start):
    """Find shortest paths in a graph with non-negative edges."""
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    queue = [(0, start)]

    while queue:
        distance, node = heapq.heappop(queue)
        if distance != distances[node]:
            continue
        for neighbour, weight in graph[node].items():
            candidate = distance + weight
            if candidate < distances[neighbour]:
                distances[neighbour] = candidate
                heapq.heappush(queue, (candidate, neighbour))
    return distances


if __name__ == "__main__":
    graph = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C"]}
    print(breadth_first_search(graph, "A"))
    print(depth_first_search(graph, "A"))
