import time

from pynput import keyboard, mouse
import random

from minesweeper_analyzer import MinesweeperAnalyzer
from board_processor import BoardProcessor


class MinesweeperBot:

    def __init__(self, cell_size=52, replay_on_complete=False):

        self.board_processor = BoardProcessor(cell_size)
        self.analyzer = None

        self.running = True

        self.cell_size = cell_size

        self.replay_on_complete = replay_on_complete

        # Start listening to keyboard events
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()

    def play(self):
        clickedBomb = False
        while self.running and not clickedBomb:
            # Update the current state of the board
            clickedBomb = self.update_state()

            if clickedBomb:
                print("Game over!")
                # press the space key on the keyboard
                keyboard.Controller().press(keyboard.Key.space)
                time.sleep(1)

                if self.replay_on_complete:
                    self.restart()
                else:
                    self.running = False
                    return  # Stop the game

            # Look for chord clicking opportunities
            chord_moves = self.analyzer.find_chord_moves()
            if chord_moves:
                x, y = chord_moves[0]
                print(f"Performing chord click at ({x}, {y})")
                self.click_cell(y, x)
                time.sleep(0.5 + random.random())
                continue

            # Find safe moves
            safe_moves = self.analyzer.find_safe_moves()
            if safe_moves:
                x, y = safe_moves[0]
                print(f"Making safe move at ({x}, {y})")
                self.click_cell(y, x)  # Note: click_cell takes (col, row)
                time.sleep(0.5 + random.random())
                continue

            # Find definite mines and flag them
            mines = self.analyzer.find_definite_mines()
            for x, y in mines:
                if self.board_processor.game_grid[x][y] != -1:  # Check if it's not already marked as a mine````
                    print(f"Flagging mine at ({x}, {y})")
                    self.click_cell(y, x, flag=True)  # Flag the cell
                    self.board_processor.game_grid[x][y] = -1  # Mark as mine
                    time.sleep(0.5 + random.random())

            # If no safe moves, make the lowest risk move
            best_move = self.analyzer.find_lowest_risk_move()
            if best_move:
                x, y = best_move
                print(f"Making probabilistic move at ({x}, {y})")
                self.click_cell(y, x)  # Note: click_cell takes (col, row)
            else:
                # If no moves available, try a random corner or edge cell
                unclicked = [(i, j) for i in range(self.board_processor.rows) for j in range(self.board_processor.columns)
                             if self.board_processor.game_grid[i][j] is None]
                if unclicked:
                    x, y = random.choice(unclicked)
                    print(f"Making random move at ({x}, {y})")
                    self.click_cell(y, x)
                else:
                    print("Game complete!")
                    # press the space key on the keyboard
                    keyboard.Controller().press(keyboard.Key.space)
                    self.running = True
                    self.restart()
                    self.play()
                    break

            time.sleep(0.5 + random.random())  # Add delay to avoid overwhelming the game

    def init(self):
        self.board_processor.initialize_board()
        self.board_processor.update_game_board()

        self.analyzer = MinesweeperAnalyzer(self.board_processor.game_grid, self.board_processor.rows, self.board_processor.columns)

    def update_state(self):
        clickedBomb = not self.board_processor.update_game_board()
        self.analyzer.grid = self.board_processor.game_grid
        return clickedBomb

    def restart(self):
        self.running = True
        self.board_processor.cleanup()
        self.board_processor.initialize_board()
        self.board_processor.update_game_board()
        self.play()

    def on_release(self, key):
        if key == keyboard.KeyCode.from_char('`'):  # Tilde key````````````
            # Capture the mouse position when F2 is released
            x, y = mouse.Controller().position
            self.board_processor.corners.append((x, y))

            # Check if we have selected 2 corners (top-left and bottom-right)
            if len(self.board_processor.corners) == 2:
                self.init()
                self.play()
                return False  # Stop listener after capturing corners
        elif key == keyboard.Key.esc:
            self.running = False
            return False

    def click_cell(self, x, y, flag=False):
        mouse.Controller().position = (
        self.board_processor.corners[0][0] + x * self.cell_size + self.cell_size // 2, self.board_processor.corners[0][1] + y * self.cell_size + self.cell_size // 2)
        mouse.Controller().click(mouse.Button.left if not flag else mouse.Button.right)
        if flag:
            self.board_processor.flag_positions.append((y, x))
