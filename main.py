from board_processor import BoardProcessor
from minesweeper_analyzer import MinesweeperAnalyzer

from minesweeper_assistant import MinesweeperAssistant


def main():
    board_processor: BoardProcessor = BoardProcessor(cell_size=52)
    minesweeper_analyzer: MinesweeperAnalyzer = MinesweeperAnalyzer(board_processor.game_grid, board_processor.rows, board_processor.columns)
    minesweeper_assistant: MinesweeperAssistant = MinesweeperAssistant()

    minesweeper_assistant.run()

if __name__ == '__main__':
    main()
