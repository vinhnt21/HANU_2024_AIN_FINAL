# Project Report: Degrees

---

## 1. Requirements & Code Base Structure

### Requirements
The project finds the **shortest path** between two actors based on shared movies, called "degrees of separation."

- **Example**: Input "Tom Cruise" and "Jim Carrey." The program finds the shortest link:
  - **Output**: "1 degree of separation" if they share a movie directly, otherwise shows actors connecting them indirectly.

### Code Base Structure

1. **`util.py`**:
   - **Node**: Holds information like `state` (actor ID), `parent`, and `action` (movie ID).
     - **Example**: For "Jim Carrey," the `Node` contains his ID, the previous actor, and the connecting movie.
   - **QueueFrontier**: Manages nodes for BFS search.
     - **Example**: When searching from "Tom Cruise," QueueFrontier will add actors he worked with in each movie.

2. **`degrees.py`**:
   - **load_data**: Loads CSV files into `people`, `movies`, and `names` dictionaries.
     - **Example**: "Tom Cruise" is saved with his ID, birth year, and movies he starred in.
   - **person_id_for_name**: Matches a name to a unique ID.
     - **Example**: Input "Chris Evans." If multiple results, it prompts to select the correct one.
   - **neighbors_for_person**: Finds actors connected through movies.
     - **Example**: For "Jim Carrey," it finds co-stars in "The Mask" or "Liar Liar."
   - **shortest_path**: Core BFS function to find the shortest connection path.
     - **Example**: To link "Tom Cruise" and "Jim Carrey," it outputs a list of movies and actors connecting them.

---

## 2. Initial Approach & Limitations

### Initial Approach: BFS with `while` Loop

The first solution used a **Breadth-First Search (BFS)** approach. This approach was implemented using a `while` loop to explore all possible connections from the source actor to the target. Below is the initial code for the `shortest_path` function using BFS.

#### Code

```python
def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Initialize the frontier with the starting position
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    # Loop until we find the solution or exhaust the frontier
    while not frontier.empty():
        # Remove a node from the frontier
        node = frontier.remove()

        # If this node's state is the target, we have found the path
        if node.state == target:
            # Build the path by following parent nodes back to the source
            path = []
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            path.reverse()  # Reverse the path to go from source to target
            return path

        # Mark this node as explored
        explored.add(node.state)

        # Add neighbors to the frontier
        for movie_id, person_id in neighbors_for_person(node.state):
            if not frontier.contains_state(person_id) and person_id not in explored:
                child = Node(state=person_id, parent=node, action=movie_id)
                frontier.add(child)

    # If no path is found
    return None
```

#### Explanation

- **Frontier Expansion**: Each iteration removes a node from the `frontier` (a queue of nodes to be explored). This is the actor currently being analyzed. If this actor is the target, the path is complete, and the function returns the path.
  - **Example**: Starting with "Tom Cruise," the program adds all actors he has worked with in any movie to the `frontier`. If the target actor appears, the function ends.

- **Neighbor Addition**: For each actor, the program checks their co-stars by adding them as nodes in the `frontier`. This step helps explore all potential connections.
  - **Example**: If "Tom Cruise" starred in "Top Gun" with "Val Kilmer," then "Val Kilmer" is added to the `frontier`.

#### Limitations
This `while` loop-based BFS approach faced challenges with actors who have **distant connections**, such as:

- **Example**: Searching for a path between "Ingmar Bergman" and "Nino Rota" took a long time. These actors lack direct or near-direct connections, requiring extensive exploration of nodes. The single-direction search exhaustively checks all potential paths before finding any link, making it inefficient for complex networks.

## 3. Optimized With Bidirectional Search

### Bidirectional Search Solution

To improve search speed, we implemented **Bidirectional Search**. This approach performs two simultaneous searches, one from the source and another from the target, meeting in the middle. Below is the modified `shortest_path` function using bidirectional search.

#### Code

```python
def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target using bidirectional search.

    If no possible path, returns None.
    """
    # Early exit if source and target are the same
    if source == target:
        return []

    # Initialize frontiers for bidirectional search
    frontier_forward = QueueFrontier()
    frontier_backward = QueueFrontier()
    frontier_forward.add(Node(state=source, parent=None, action=None))
    frontier_backward.add(Node(state=target, parent=None, action=None))

    # Track explored states in both directions
    explored_forward = {}
    explored_backward = {}

    # Loop until either frontier is empty or paths meet
    while not frontier_forward.empty() and not frontier_backward.empty():

        # Expand the forward frontier
        path = search_step(frontier_forward, explored_forward, explored_backward, direction="forward")
        if path is not None:
            return path

        # Expand the backward frontier
        path = search_step(frontier_backward, explored_backward, explored_forward, direction="backward")
        if path is not None:
            return path

    # If no path is found
    return None


def search_step(frontier, explored, other_explored, direction):
    """
    Performs a single step in the search for bidirectional search.
    Checks if there is a path by seeing if the node in the frontier
    intersects with nodes explored in the opposite direction.
    """
    if frontier.empty():
        return None

    node = frontier.remove()
    explored[node.state] = node  # Mark node as explored

    # Check if this node connects with the other search
    if node.state in other_explored:
        # Found a connection point
        path = build_path(node, other_explored[node.state], direction)
        return path

    # Expand neighbors
    for movie_id, person_id in neighbors_for_person(node.state):
        if person_id not in explored and not frontier.contains_state(person_id):
            child = Node(state=person_id, parent=node, action=movie_id)
            frontier.add(child)

    return None


def build_path(node_forward, node_backward, direction):
    """
    Builds the path from source to target by connecting the nodes
    from the forward and backward searches at the intersection point.
    """
    # Path from start to intersection
    path_forward = []
    node = node_forward
    while node.parent is not None:
        path_forward.append((node.action, node.state))
        node = node.parent
    path_forward.reverse()  # Make it go from source to intersection

    # Path from intersection to end
    path_backward = []
    node = node_backward
    while node.parent is not None:
        path_backward.append((node.action, node.state))
        node = node.parent

    # Merge paths, considering the search direction
    if direction == "forward":
        return path_forward + path_backward
    else:
        return path_backward + path_forward
```

#### Explanation

1. **Two Frontiers**: The search starts from both the source and target, with `frontier_forward` and `frontier_backward` representing each direction.
   - **Example**: If searching between "Tom Cruise" and "Jim Carrey," one frontier starts from "Tom Cruise" and the other from "Jim Carrey."

2. **Explored Sets**: Each frontier has an explored set to avoid redundancy. The function `search_step` checks if the current node in one search intersects with nodes explored in the other search.
   - **Example**: While expanding from "Tom Cruise," actors he’s connected to are stored in `explored_forward`. Similarly, "Jim Carrey"’s connections are tracked in `explored_backward`.

3. **Alternating Expansion**: The algorithm alternates between expanding nodes from each frontier. This method stops when nodes in the two frontiers meet.
   - **Example**: The search might find a common actor, like "Nicole Kidman," linking "Tom Cruise" to "Jim Carrey."

4. **Path Construction**: When a common node is found, `build_path` combines paths from the forward and backward searches to form the full path.
   - **Example**: If "Nicole Kidman" connects "Tom Cruise" and "Jim Carrey" through "Eyes Wide Shut" and "Batman Forever," the function combines these steps to show "1 degree of separation."

### Advantages
Bidirectional Search reduces the search space by meeting in the middle, halving the exploration time. This is particularly effective for high-degree connections, such as between "Ingmar Bergman" and "Nino Rota," allowing for faster and more efficient results on large datasets.

