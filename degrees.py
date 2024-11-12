import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set(),
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set(),
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    # source = person_id_for_name(input("Name: "))
    # source = person_id_for_name("Emma Watson")
    source = person_id_for_name("Ingmar Bergman")
    if source is None:
        sys.exit("Person not found.")
    # target = person_id_for_name(input("Name: "))
    # target = person_id_for_name("Jennifer Lawrence")
    target = person_id_for_name("Nino Rota")
    if target is None:
        sys.exit("Person not found.")

    # start time
    import time

    start = time.time()
    # path = shortest_path_bfs_simple(source, target)
    path = shortest_path_bfs_pruning(source, target)
    # path = shortest_path_bidirectional(source, target)
    end = time.time()
    print(f"Execution time: {end - start} seconds.")
    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path_bfs_simple(source, target):
    """
    Finds the shortest path between two nodes (source and target) using BFS.
    """
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)
    explored = set()
    steps = 0  # Step counter

    while not frontier.empty():
        steps += 1
        print(
            f"Step {steps}, Frontier size: {len(frontier.frontier)}, state {frontier.frontier[0].state}"
        )
        node = frontier.remove()

        if node.state == target:
            path = []
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            path.reverse()
            print(f"Path found in {steps} steps.")
            return path

        explored.add(node.state)

        for movie_id, person_id in neighbors_for_person(node.state):
            if not frontier.contains_state(person_id) and person_id not in explored:
                child = Node(state=person_id, parent=node, action=movie_id)
                frontier.add(child)

    print(f"No path found after {steps} steps.")
    return None


def shortest_path_bfs_pruning(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs that connect the source to the target using BFS with pruning.
    """
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)
    explored = set()
    shortest_paths = {source: 0}
    steps = 0  # Step counter

    while not frontier.empty():
        node = frontier.remove()
        steps += 1
        print(f"Step {steps}: {node.state}")

        if node.state == target:
            path = []
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            path.reverse()
            print(f"Path found in {steps} steps.")
            return path

        explored.add(node.state)

        for movie_id, person_id in neighbors_for_person(node.state):
            new_path_length = shortest_paths[node.state] + 1
            if person_id not in explored and (
                person_id not in shortest_paths
                or new_path_length < shortest_paths[person_id]
            ):
                shortest_paths[person_id] = new_path_length
                child = Node(state=person_id, parent=node, action=movie_id)
                frontier.add(child)

    print(f"No path found after {steps} steps.")
    return None


def shortest_path_bidirectional(source, target):
    start_frontier, goal_frontier = initialize_frontiers(source, target)
    start_explored, goal_explored = initialize_explored_dicts(source, target)
    steps = 0  # Step counter
    while not start_frontier.empty() and not goal_frontier.empty():
        steps += 1
        result = search_step(start_frontier, start_explored, goal_explored, "forward")
        if result:
            print(f"Path found in {steps} steps.")
            return result

        result = search_step(goal_frontier, goal_explored, start_explored, "backward")
        if result:
            print(f"Path found in {steps} steps.")
            return result

    print(f"No path found after {steps} steps.")
    return None


def initialize_frontiers(source, target):
    start_frontier = QueueFrontier()
    goal_frontier = QueueFrontier()
    start_frontier.add(Node(state=source, parent=None, action=None))
    goal_frontier.add(Node(state=target, parent=None, action=None))
    return start_frontier, goal_frontier


def initialize_explored_dicts(source, target):
    start_explored = {source: None}
    goal_explored = {target: None}
    return start_explored, goal_explored


def search_step(frontier, explored, other_explored, direction):
    if frontier.empty():
        return None

    node = frontier.remove()
    explored[node.state] = node

    if node.state in other_explored:
        path = build_path(node, other_explored[node.state], direction)
        return path

    for movie_id, person_id in neighbors_for_person(node.state):
        if person_id not in explored and not frontier.contains_state(person_id):
            child = Node(state=person_id, parent=node, action=movie_id)
            frontier.add(child)

    return None


def build_path(node_forward, node_backward, direction):
    path_forward = []
    node = node_forward
    while node.parent is not None:
        path_forward.append((node.action, node.state))
        node = node.parent
    path_forward.reverse()

    path_backward = []
    node = node_backward
    while node.parent is not None:
        path_backward.append((node.action, node.state))
        node = node.parent

    if direction == "forward":
        return path_forward + path_backward
    else:
        return path_backward + path_forward


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
