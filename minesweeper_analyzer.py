class MinesweeperAnalyzer:
    def __init__(self, grid, rows, cols):
        self.grid = grid
        self.rows = rows
        self.cols = cols

    def update(self, grid):
        self.grid = grid

    def print_board(self):
        for row in self.grid:
            for cell in row:
                if cell is None:
                    print('-', end=' ')
                else:
                    print(cell, end=' ')
            print()

    def get_adjacent_cells(self, x, y):
        """Returns all valid adjacent cells coordinates."""
        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
                    adjacent.append((new_x, new_y))
        return adjacent

    def count_adjacent_mines(self, x, y):
        """Count known mines and unknown cells around a given cell."""
        unknown = 0
        mines = 0
        for adj_x, adj_y in self.get_adjacent_cells(x, y):
            if self.grid[adj_x][adj_y] is None:
                unknown += 1
            elif self.grid[adj_x][adj_y] == -1:  # We'll use -1 to mark known mines
                mines += 1
        return mines, unknown

    def find_safe_moves(self):
        """Find definitively safe moves based on number constraints."""
        safe_moves = []
        for x in range(self.rows):
            for y in range(self.cols):
                if self.grid[x][y] is not None and self.grid[x][y] > 0:  # If it's a number
                    mines, unknown = self.count_adjacent_mines(x, y)
                    # If all mines are accounted for, remaining unknown cells are safe
                    if mines == self.grid[x][y]:
                        for adj_x, adj_y in self.get_adjacent_cells(x, y):
                            if self.grid[adj_x][adj_y] is None:
                                safe_moves.append((adj_x, adj_y))
        return list(set(safe_moves))  # Remove duplicates

    def find_definite_mines(self):
        """Find cells that must be mines based on number constraints."""
        mines = []
        for x in range(self.rows):
            for y in range(self.cols):
                if self.grid[x][y] is not None and self.grid[x][y] > 0:
                    mines_found, unknown = self.count_adjacent_mines(x, y)
                    # If remaining unknown cells must all be mines
                    if unknown > 0 and self.grid[x][y] - mines_found == unknown:
                        for adj_x, adj_y in self.get_adjacent_cells(x, y):
                            if self.grid[adj_x][adj_y] is None:
                                mines.append((adj_x, adj_y))
        return list(set(mines))

    def find_lowest_risk_move(self):
        """Find the move with lowest probability of being a mine."""
        min_risk = float('inf')
        best_move = None

        # Check each unknown cell
        for x in range(self.rows):
            for y in range(self.cols):
                if self.grid[x][y] is None:
                    max_risk = 0
                    valid_constraint = False

                    # Check all adjacent revealed numbers
                    for adj_x, adj_y in self.get_adjacent_cells(x, y):
                        if self.grid[adj_x][adj_y] is not None and self.grid[adj_x][adj_y] > 0:
                            mines, unknown = self.count_adjacent_mines(adj_x, adj_y)
                            if unknown > 0:
                                valid_constraint = True
                                risk = (self.grid[adj_x][adj_y] - mines) / unknown
                                max_risk = max(max_risk, risk)

                    if valid_constraint and max_risk < min_risk:
                        min_risk = max_risk
                        best_move = (x, y)

        print("Risk of best move: ", min_risk)
        return best_move

    def find_chord_moves(self):
        """Find cells where we can perform a chord click."""
        chord_moves = []
        for x in range(self.rows):
            for y in range(self.cols):
                if self.grid[x][y] is not None and self.grid[x][y] > 0:  # If it's a number
                    mines, unknown = self.count_adjacent_mines(x, y)
                    # If the number matches exactly the number of adjacent flags
                    if mines == self.grid[x][y] and unknown > 0:
                        chord_moves.append((x, y))
        return chord_moves
