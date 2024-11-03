## 1. Requirements & Code Base Structure

### Requirements

The project finds the **shortest path** between two actors based on shared movies, called "degrees of separation."

- **Example**: Input "Tom Cruise" and "Jim Carrey." The program finds the shortest link:
    - **Output**: "1 degree of separation" if they share a movie directly, otherwise shows actors connecting them
      indirectly.

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

## 2. Một số thuật toán tìm kiếm phổ biến

| Thuật toán           | Ý tưởng                                              | Ưu điểm                                   | Nhược điểm                           | Ví dụ                                                     |
|----------------------|------------------------------------------------------|-------------------------------------------|--------------------------------------|-----------------------------------------------------------|
| Depth-First Search   | Tìm sâu nhất có thể trước, quay lại khi cần          | Tiết kiệm bộ nhớ                          | Không đảm bảo đường ngắn nhất        | Duyệt mê cung bằng cách đi hết 1 hướng trước khi quay lại |
| Breadth-First Search | Tìm từng mức theo chiều rộng trước khi tiến sâu      | Đảm bảo đường ngắn nhất                   | Tốn nhiều bộ nhớ khi không gian rộng | Tìm đường trong mê cung bằng cách tìm ở các ô gần trước   |
| Greedy Best-First    | Chọn bước ước lượng gần đích nhất                    | Nhanh nếu heuristic tốt                   | Không đảm bảo đường ngắn nhất        | Đi theo lối đi có vẻ ngắn nhất trong mê cung              |
| A*                   | Kết hợp chi phí thực tế và ước lượng đến đích        | Đảm bảo đường ngắn nhất nếu heuristic tốt | Tốn nhiều bộ nhớ                     | Tìm đường tối ưu từ nhà đến nơi làm việc trên bản đồ GPS  |
| Minimax              | Tìm nước đi tối ưu giả định đối thủ cũng chơi tối ưu | Tìm chiến lược tốt nhất trong trò chơi    | Tốn tài nguyên khi nhiều khả năng    | Tìm nước đi tốt nhất trong trò chơi cờ caro               |
| Alpha-Beta Pruning   | Loại bỏ các nhánh không cần thiết trong Minimax      | Giảm số lượng nút cần xem xét             | Cần tối ưu để hiệu quả               | Loại bỏ các nước đi không tối ưu trong cờ vua             |

## 3. Lí do chọn Breadth-First Search cho vấn đề Degrees

- **Đảm bảo đường đi ngắn nhất**: Tìm theo từng mức khoảng cách.
- **Dễ triển khai**: Sử dụng hàng đợi, quản lý các nút có hệ thống.
- **Phù hợp với không gian lớn**: Không đi quá sâu vào các nhánh xa.
- **Không cần hàm heuristic**: Đơn giản hóa, không cần ước lượng chi phí.

### Cách tiếp cận ban đầu:

- **BFS với vòng lặp `while`**: Sử dụng BFS với vòng lặp `while` để khám phá tất cả các kết nối có thể từ diễn viên
  nguồn đến mục tiêu. Dưới đây là mã nguồn ban đầu cho hàm `shortest_path` sử dụng BFS.
- **Mã nguồn ban đầu**:

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
- **Giải thích**:
    - **Khởi tạo**: Bắt đầu từ diễn viên nguồn, thêm vào hàng đợi `frontier`.
    - **Khám phá**: Lặp qua các nút trong `frontier` cho đến khi tìm thấy diễn viên mục tiêu.
    - **Xử lý**: Nếu tìm thấy diễn viên mục tiêu, xây dựng đường dẫn từ diễn viên nguồn đến mục tiêu.
    - **Mở rộng**: Thêm các diễn viên kề vào `frontier` nếu chưa được khám phá.
    - **Kết quả**: Trả về đường dẫn hoặc `None` nếu không tìm thấy.

### Hạn chế của cách làm trên:

- **Tốn thời gian**: Cần duyệt qua tất cả các kết nối có thể.
- **Tốn bộ nhớ**: Lưu trữ tất cả các diễn viên đã khám phá.
- **Không hiệu quả**: Không tận dụng thông tin để cắt bớt các kết nối không cần thiết.
- **Không linh hoạt**: Khó mở rộng để tìm kiếm nhiều kết nối cùng lúc.
- **Example**: Searching for a path between "Ingmar Bergman" and "Nino Rota" took a long time. These actors lack direct
  or near-direct connections, requiring extensive exploration of nodes. The single-direction search exhaustively checks
  all potential paths before finding any link, making it inefficient for complex networks.

## 4. Cải tiến: Breadth-First Search với Cắt Nhánh
