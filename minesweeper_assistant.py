import time

import pyautogui
from pynput import keyboard, mouse
from pynput.keyboard import Key

from board_processor import BoardProcessor
from minesweeper_analyzer import MinesweeperAnalyzer

import tkinter as tk


class MinesweeperAssistant:
    def __init__(self):
        self.running = True

        # Initialize the main window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window initially

        # Initialize components
        self.board_processor = BoardProcessor()
        self.analyzer = None

        # State variables
        self.corner_count = 0
        self.is_initialized = False
        self.hovered_rectangles = set()

        # Create canvas (will be configured after corners are selected)
        self.canvas = tk.Canvas(self.root, bd=0, highlightthickness=1, bg='black')
        self.canvas.pack(fill='both', expand=True)

        # Configure window properties
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.wm_attributes("-topmost", 1)
        self.root.overrideredirect(True)  # Remove window decorations

        # Storage for rectangles
        self.mine_rectangles = []  # Store red rectangles (mines)
        self.safe_rectangles = []  # Store green rectangles (safe moves)
        self.chord_rectangles = []  # Store blue rectangles (chord moves)

        # Initialize input listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )

        # Start listeners
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def on_key_press(self, key):
        try:
            if key.char == '`' and not self.is_initialized:
                if self.corner_count == 0:
                    # Get first corner
                    x, y = pyautogui.position()
                    self.board_processor.corners = [(x, y)]
                    self.corner_count += 1
                    print("Top-left corner captured")
                elif self.corner_count == 1:
                    # Get second corner and initialize
                    x, y = pyautogui.position()
                    self.board_processor.corners.append((x, y))
                    print("Bottom-right corner captured")
                    self.initialize_window()

        except AttributeError:
            if key == Key.space:
                print("Resetting the game")
                for rect in self.mine_rectangles + self.safe_rectangles + self.chord_rectangles:
                    self.canvas.delete(rect)
                self.mine_rectangles = []
                self.safe_rectangles = []
                self.chord_rectangles = []
                self.hovered_rectangles = set()
                self.board_processor.flag_positions = []
                self.running = True
            pass

    def on_mouse_move(self, x, y):
        if not self.is_initialized:
            return

        # Convert screen coordinates to window coordinates
        window_x = x - self.board_processor.corners[0][0]
        window_y = y - self.board_processor.corners[0][1]

        # Check if mouse is within window bounds
        if not (0 <= window_x <= self.canvas.winfo_width() and
                0 <= window_y <= self.canvas.winfo_height()):
            self.on_mouse_leave()
            return

        cell_size = self.board_processor.cell_size

        # Hide/show rectangles based on mouse position
        for rect in self.mine_rectangles + self.safe_rectangles + self.chord_rectangles:
            coords = self.canvas.coords(rect)
            if len(coords) != 4:
                continue  # in case weird bugs happen

            if coords[0] <= window_x <= coords[2] and coords[1] <= window_y <= coords[3]:
                self.canvas.itemconfig(rect, fill='black')
                self.hovered_rectangles.add(rect)
            elif rect in self.hovered_rectangles:
                # Restore original color based on rectangle type
                if rect in self.mine_rectangles:
                    self.canvas.itemconfig(rect, fill='red')
                elif rect in self.safe_rectangles:
                    self.canvas.itemconfig(rect, fill='green')
                elif rect in self.chord_rectangles:
                    self.canvas.itemconfig(rect, fill='blue')
                self.hovered_rectangles.remove(rect)

    def on_mouse_leave(self):
        # Restore all hovered rectangles to their original colors
        for rect in self.hovered_rectangles:
            if rect in self.mine_rectangles:
                self.canvas.itemconfig(rect, fill='red')
            elif rect in self.safe_rectangles:
                self.canvas.itemconfig(rect, fill='green')
            elif rect in self.chord_rectangles:
                self.canvas.itemconfig(rect, fill='blue')
        self.hovered_rectangles.clear()

    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_initialized:
            return

        # Convert screen coordinates to window coordinates
        window_x = x - self.board_processor.corners[0][0]
        window_y = y - self.board_processor.corners[0][1]

        # Check if click is within window bounds
        if not (0 <= window_x <= self.canvas.winfo_width() and
                0 <= window_y <= self.canvas.winfo_height()):
            return

        cell_size = self.board_processor.cell_size
        row = window_y // cell_size
        col = window_x // cell_size


        if pressed and button == mouse.Button.right and (self.board_processor.game_grid[row][col] is None or self.board_processor.game_grid[row][col] < 0):
            # Toggle flag in board processor
            flag_pos = (row, col)
            if flag_pos in self.board_processor.flag_positions:
                self.board_processor.flag_positions.remove(flag_pos)
                print(f"Removed flag at {flag_pos}")
            else:
                self.board_processor.flag_positions.append(flag_pos)
                print(f"Added flag at {flag_pos}")

        # Update game state before processing the click
        if not self.board_processor.update_game_board():
            self.root.quit()  # Exit if game is over (bomb found)
            return

        if not pressed:
            self.root.after(250, self.update_overlay)

    def initialize_window(self):
        # Initialize board processor with corners
        self.board_processor.initialize_board()

        # Configure window size and position
        top_left = self.board_processor.corners[0]
        bottom_right = self.board_processor.corners[1]

        # Calculate width and height including the last row and column
        width = (self.board_processor.columns * self.board_processor.cell_size)
        height = (self.board_processor.rows * self.board_processor.cell_size)

        # Position and show window
        self.root.geometry(f"{width}x{height}+{top_left[0]}+{top_left[1]}")
        self.canvas.configure(width=width, height=height)
        self.root.deiconify()

        # Initialize analyzer
        self.analyzer = MinesweeperAnalyzer(
            self.board_processor.game_grid,
            self.board_processor.rows,
            self.board_processor.columns
        )

        self.is_initialized = True

        # self.update_overlay()
        self.root.after(250, self.update_overlay)

    def update_overlay(self):
        # Clear existing rectangles
        for rect in self.mine_rectangles + self.safe_rectangles + self.chord_rectangles:
            self.canvas.delete(rect)
        self.mine_rectangles.clear()
        self.safe_rectangles.clear()
        self.chord_rectangles.clear()

        # Update game state
        if not self.running:
            # clean the ui square lists
            for rect in self.mine_rectangles + self.safe_rectangles + self.chord_rectangles:
                self.canvas.delete(rect)
            self.board_processor.flag_positions = []
            self.mine_rectangles = []
            self.safe_rectangles = []
            self.chord_rectangles = []
            self.hovered_rectangles = set()
            self.running = False
            return

        self.board_processor.update_game_board()

        self.analyzer.update(self.board_processor.game_grid)

        cell_size = self.board_processor.cell_size

        # Draw mines (red)
        mines = self.analyzer.find_definite_mines()
        for row, col in mines:
            rect = self.canvas.create_rectangle(
                col * cell_size, row * cell_size,
                (col + 1) * cell_size, (row + 1) * cell_size,
                fill='red', stipple='gray50'
            )
            self.mine_rectangles.append(rect)

        # Draw safe moves (green)
        safe_moves = self.analyzer.find_safe_moves()
        for row, col in safe_moves:
            rect = self.canvas.create_rectangle(
                col * cell_size, row * cell_size,
                (col + 1) * cell_size, (row + 1) * cell_size,
                fill='green', stipple='gray50'
            )
            self.safe_rectangles.append(rect)

        # Draw chord moves (blue)
        chord_moves = self.analyzer.find_chord_moves()
        for row, col in chord_moves:
            rect = self.canvas.create_rectangle(
                col * cell_size, row * cell_size,
                (col + 1) * cell_size, (row + 1) * cell_size,
                fill='blue', stipple='gray50'
            )
            self.chord_rectangles.append(rect)

    def cleanup(self):
        # Stop listeners
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.root.quit()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.cleanup()
