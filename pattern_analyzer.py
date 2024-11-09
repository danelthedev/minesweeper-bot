class PatternAnalyzer:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def find_diagonal_pattern(self):
        """
        Find diagonal pattern like:
        1 2
        2 1
        Where corners can be determined safe or mines.
        """
        safe_moves = []
        mines = []

        for x in range(self.analyzer.rows - 1):
            for y in range(self.analyzer.cols - 1):
                # Check if we have a 2x2 grid of numbers
                values = [
                    self.analyzer.grid[x][y],
                    self.analyzer.grid[x][y + 1],
                    self.analyzer.grid[x + 1][y],
                    self.analyzer.grid[x + 1][y + 1]
                ]

                # Skip if any cell isn't a number
                if any(v is None or v == -1 for v in values):
                    continue

                # Check for 1-2-2-1 diagonal pattern
                if ((values[0] == 1 and values[3] == 1 and values[1] == 2 and values[2] == 2) or
                        (values[1] == 1 and values[2] == 1 and values[0] == 2 and values[3] == 2)):

                    # Count flags around each number to ensure we haven't already found mines
                    flags = [0] * 4
                    positions = [(x, y), (x, y + 1), (x + 1, y), (x + 1, y + 1)]

                    for i, pos in enumerate(positions):
                        for adj_x, adj_y in self.analyzer.get_adjacent_cells(*pos):
                            if self.analyzer.grid[adj_x][adj_y] == -1:
                                flags[i] += 1

                    # Only proceed if pattern is still unsolved
                    if all(f == 0 for f in flags):
                        if values[0] == 1 and values[3] == 1:  # 1-2-2-1 pattern
                            safe_moves.extend([(x, y + 1), (x + 1, y)])  # Corners are safe
                            mines.extend([(x, y), (x + 1, y + 1)])  # Edges are mines
                        else:  # 2-1-1-2 pattern
                            safe_moves.extend([(x, y), (x + 1, y + 1)])  # Edges are safe
                            mines.extend([(x, y + 1), (x + 1, y)])  # Corners are mines

        return list(set(safe_moves)), list(set(mines))

    def find_box_pattern(self):
        """
        Find 2x3 or 3x2 box patterns like:
        2 3 2
        2 3 2
        Where middle edges must be mines
        """
        mines = []

        # Check horizontal boxes (2x3)
        for x in range(self.analyzer.rows - 1):
            for y in range(self.analyzer.cols - 2):
                values = [
                    [self.analyzer.grid[x][y], self.analyzer.grid[x][y + 1], self.analyzer.grid[x][y + 2]],
                    [self.analyzer.grid[x + 1][y], self.analyzer.grid[x + 1][y + 1], self.analyzer.grid[x + 1][y + 2]]
                ]

                # Check for 2-3-2 pattern in both rows
                if all(v is not None and v != -1 for row in values for v in row):
                    if (values[0] == [2, 3, 2] and values[1] == [2, 3, 2]):
                        # Check that we haven't already found mines
                        if not any(self.analyzer.grid[x - 1][y + 1] == -1 if x > 0 else False or
                                                                                        self.analyzer.grid[x + 2][
                                                                                            y + 1] == -1 if x < self.analyzer.rows - 2 else False):
                            # Middle edges must be mines
                            if x > 0:
                                mines.append((x - 1, y + 1))
                            if x < self.analyzer.rows - 2:
                                mines.append((x + 2, y + 1))

        # Check vertical boxes (3x2)
        for x in range(self.analyzer.rows - 2):
            for y in range(self.analyzer.cols - 1):
                values = [
                    [self.analyzer.grid[x][y], self.analyzer.grid[x][y + 1]],
                    [self.analyzer.grid[x + 1][y], self.analyzer.grid[x + 1][y + 1]],
                    [self.analyzer.grid[x + 2][y], self.analyzer.grid[x + 2][y + 1]]
                ]

                # Check for 2-3-2 pattern in both columns
                if all(v is not None and v != -1 for row in values for v in row):
                    if ([row[0] for row in values] == [2, 3, 2] and
                            [row[1] for row in values] == [2, 3, 2]):
                        # Check that we haven't already found mines
                        if not any(self.analyzer.grid[x + 1][y - 1] == -1 if y > 0 else False or
                                                                                        self.analyzer.grid[x + 1][
                                                                                            y + 2] == -1 if y < self.analyzer.cols - 2 else False):
                            # Middle edges must be mines
                            if y > 0:
                                mines.append((x + 1, y - 1))
                            if y < self.analyzer.cols - 2:
                                mines.append((x + 1, y + 2))

        return list(set(mines))

    def find_121_pattern(self):
        """
        Find 1-2-1 patterns like:
        1 2 1
        Where the cells adjacent to both 1s (diagonally touching the 2) must be mines.
        Returns list of mine positions.
        """
        mines = []

        # Check horizontal 1-2-1 patterns
        for x in range(self.analyzer.rows):
            for y in range(self.analyzer.cols - 2):
                # Get the three consecutive cells
                values = [
                    self.analyzer.grid[x][y],
                    self.analyzer.grid[x][y + 1],
                    self.analyzer.grid[x][y + 2]
                ]

                # Check if we have a 1-2-1 pattern
                if values == [1, 2, 1]:
                    # Count existing flags around each number
                    flags = [0] * 3
                    for i, y_pos in enumerate(range(y, y + 3)):
                        for adj_x, adj_y in self.analyzer.get_adjacent_cells(x, y_pos):
                            if self.analyzer.grid[adj_x][adj_y] == -1:
                                flags[i] += 1

                    # If pattern is unsolved
                    if all(f == 0 for f in flags):
                        # Add mines diagonally adjacent to both 1s (touching the 2)
                        if x > 0:  # Check cells above
                            if self.analyzer.grid[x - 1][y] is None:
                                mines.append((x - 1, y))  # Above left 1
                            if self.analyzer.grid[x - 1][y + 2] is None:
                                mines.append((x - 1, y + 2))  # Above right 1
                        if x < self.analyzer.rows - 1:  # Check cells below
                            if self.analyzer.grid[x + 1][y] is None:
                                mines.append((x + 1, y))  # Below left 1
                            if self.analyzer.grid[x + 1][y + 2] is None:
                                mines.append((x + 1, y + 2))  # Below right 1

        # Check vertical 1-2-1 patterns
        for x in range(self.analyzer.rows - 2):
            for y in range(self.analyzer.cols):
                # Get the three consecutive cells
                values = [
                    self.analyzer.grid[x][y],
                    self.analyzer.grid[x + 1][y],
                    self.analyzer.grid[x + 2][y]
                ]

                # Check if we have a 1-2-1 pattern
                if values == [1, 2, 1]:
                    # Count existing flags around each number
                    flags = [0] * 3
                    for i, x_pos in enumerate(range(x, x + 3)):
                        for adj_x, adj_y in self.analyzer.get_adjacent_cells(x_pos, y):
                            if self.analyzer.grid[adj_x][adj_y] == -1:
                                flags[i] += 1

                    # If pattern is unsolved
                    if all(f == 0 for f in flags):
                        # Add mines diagonally adjacent to both 1s (touching the 2)
                        if y > 0:  # Check cells to the left
                            if self.analyzer.grid[x][y - 1] is None:
                                mines.append((x, y - 1))  # Left of top 1
                            if self.analyzer.grid[x + 2][y - 1] is None:
                                mines.append((x + 2, y - 1))  # Left of bottom 1
                        if y < self.analyzer.cols - 1:  # Check cells to the right
                            if self.analyzer.grid[x][y + 1] is None:
                                mines.append((x, y + 1))  # Right of top 1
                            if self.analyzer.grid[x + 2][y + 1] is None:
                                mines.append((x + 2, y + 1))  # Right of bottom 1

        return list(set(mines))

    def analyze_patterns(self):
        """Analyze all advanced patterns and return combined results."""
        all_safe_moves = []
        all_mines = []

        # Find diagonal patterns
        safe_diagonal, mines_diagonal = self.find_diagonal_pattern()
        all_safe_moves.extend(safe_diagonal)
        all_mines.extend(mines_diagonal)

        # Find box patterns
        mines_box = self.find_box_pattern()
        all_mines.extend(mines_box)

        # Find 1-2-1 patterns
        mines_121 = self.find_121_pattern()
        all_mines.extend(mines_121)

        return list(set(all_safe_moves)), list(set(all_mines))