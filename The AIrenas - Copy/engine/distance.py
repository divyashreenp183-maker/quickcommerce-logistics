"""
Distance and routing utilities for the NeuralOps Logistics System.
Provides Haversine distance calculations and Dijkstra-based shortest path routing.
"""
import math
import heapq
from typing import Dict, List, Optional, Tuple


def haversine(coord1: tuple, coord2: tuple) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates.
    Returns distance in kilometers.

    Args:
        coord1: (latitude, longitude) in decimal degrees
        coord2: (latitude, longitude) in decimal degrees
    """
    R = 6371.0  # Earth's radius in km

    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def estimate_travel_time(distance_km: float, speed_kmph: float) -> float:
    """
    Estimate travel time in minutes given distance and speed.
    Adds 20% buffer for traffic/real-world conditions.

    Args:
        distance_km: Distance in kilometers
        speed_kmph: Average speed in km/h

    Returns:
        Estimated travel time in minutes
    """
    if speed_kmph <= 0:
        return float('inf')
    base_time = (distance_km / speed_kmph) * 60  # convert to minutes
    traffic_buffer = base_time * 0.20             # 20% traffic buffer
    return base_time + traffic_buffer


def build_city_graph(locations: Dict[str, tuple]) -> Dict[str, Dict[str, float]]:
    """
    Build a weighted undirected graph of locations for Dijkstra routing.
    Edges represent haversine distances between all location pairs.

    Args:
        locations: {node_name: (lat, lon)}

    Returns:
        Adjacency dict: {node: {neighbor: distance_km}}
    """
    graph = {node: {} for node in locations}
    nodes = list(locations.items())

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            name_a, coord_a = nodes[i]
            name_b, coord_b = nodes[j]
            dist = haversine(coord_a, coord_b)
            graph[name_a][name_b] = dist
            graph[name_b][name_a] = dist

    return graph


def dijkstra(graph: Dict[str, Dict[str, float]], start: str, end: str
             ) -> Tuple[float, List[str]]:
    """
    Dijkstra's algorithm to find the shortest path between two nodes.

    Args:
        graph: Adjacency dict {node: {neighbor: distance}}
        start: Source node name
        end: Destination node name

    Returns:
        (total_distance_km, path_as_list_of_nodes)
    """
    if start not in graph or end not in graph:
        return float('inf'), []

    # Priority queue: (distance, node)
    pq = [(0.0, start)]
    dist = {node: float('inf') for node in graph}
    dist[start] = 0.0
    prev = {node: None for node in graph}
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            break

        for neighbor, weight in graph[current].items():
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    if path[0] != start:
        return float('inf'), []

    return dist[end], path
