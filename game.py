import pygame
import numpy as np
import time
import sys
import random

from enums import GameState, PowerUpType, AIPersonality
from ai import AIEngine
from visualization import AlgorithmVisualizer
from ui import GameUI
import config

class EnhancedTicTacToe:
    def __init__(self):
        """Initialize the game"""
        pygame.init()
        self.WIDTH = config.WIDTH
        self.HEIGHT = config.HEIGHT
        self.BOARD_SIZE = 3
        self.CELL_SIZE = config.CELL_SIZE
        self.VISUALIZATION_WIDTH = config.VISUALIZATION_WIDTH
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Enhanced Tic-Tac-Toe")
        
        # Fonts
        self.fonts = {
            'normal': pygame.font.SysFont('Arial', 24),
            'small': pygame.font.SysFont('Arial', 16),
            'large': pygame.font.SysFont('Arial', 32, True)
        }
        
        # Colors
        self.colors = {
            'BLACK': config.BLACK,
            'WHITE': config.WHITE,
            'GRAY': config.GRAY,
            'RED': config.RED,
            'GREEN': config.GREEN,
            'BLUE': config.BLUE,
            'YELLOW': config.YELLOW,
            'PURPLE': config.PURPLE,
            'LIGHT_BLUE': (173, 216, 230),
            'LIGHT_GREEN': (144, 238, 144)
        }
        
        # Initialize components
        self.ai_engine = AIEngine(self)
        self.visualizer = AlgorithmVisualizer(self.screen, self.colors, self.fonts)
        self.ui = GameUI(self, self.screen, self.colors, self.fonts)
        
        # Game state
        self.reset_game()
        
        # UI states
        self.show_algorithm = True
        self.selected_powerup = None
        self.ai_thinking = False
        self.ai_personality = AIPersonality.BALANCED

    def reset_game(self):
        """Reset the game state"""
        self.board = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.powerups = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.player_turn = True
        self.game_state = GameState.ONGOING
        self.moves_history = []
        self.winning_line = None
        self.winning_line_animation = 0
        self.highlight_cells = []
        self.last_move = None
        
        # Reset AI engine
        if hasattr(self, 'ai_engine'):
            self.ai_engine.reset()
        
        # Add random powerups
        self.add_powerups()

    def add_powerups(self):
        """Add random powerups to the board"""
        # Clear existing powerups
        self.powerups = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        
        # Add 1-2 powerups for 3x3 board
        num_powerups = 2
        available_positions = [(x, y) for x in range(self.BOARD_SIZE) for y in range(self.BOARD_SIZE)]
        
        for _ in range(min(num_powerups, len(available_positions))):
            pos_idx = random.randint(0, len(available_positions) - 1)
            x, y = available_positions.pop(pos_idx)
            self.powerups[x][y] = random.choice([p.value for p in PowerUpType if p != PowerUpType.NONE])

    def draw_board(self):
        """Draw the game board and all elements"""
        # Clear screen
        self.screen.fill(self.colors['LIGHT_BLUE'])
        
        # Calculate board position
        board_width = self.BOARD_SIZE * self.CELL_SIZE
        board_height = self.BOARD_SIZE * self.CELL_SIZE
        board_x = (self.WIDTH - self.VISUALIZATION_WIDTH - board_width) // 2
        board_y = (self.HEIGHT - board_height) // 2
        
        # Draw board background
        board_bg_rect = pygame.Rect(board_x - 10, board_y - 10, 
                                  board_width + 20, board_height + 20)
        pygame.draw.rect(self.screen, self.colors['LIGHT_GREEN'], board_bg_rect)
        pygame.draw.rect(self.screen, self.colors['BLACK'], board_bg_rect, 3)
        
        # Draw title
        title_text = self.fonts['large'].render("Enhanced Tic-Tac-Toe", True, self.colors['BLACK'])
        self.screen.blit(title_text, (board_x, board_y - 50))
        
        # Draw grid
        for i in range(self.BOARD_SIZE+1):
            # Vertical lines
            pygame.draw.line(self.screen, self.colors['BLACK'], 
                            (board_x + i * self.CELL_SIZE, board_y), 
                            (board_x + i * self.CELL_SIZE, board_y + board_height), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, self.colors['BLACK'], 
                            (board_x, board_y + i * self.CELL_SIZE), 
                            (board_x + board_width, board_y + i * self.CELL_SIZE), 2)
        
        # Draw winning line if there is one
        if self.winning_line and self.game_state != GameState.ONGOING:
            self.draw_winning_line(board_x, board_y)
        
        # Draw board contents (X, O, powerups)
        self.draw_board_contents(board_x, board_y)
        
        # Draw UI elements
        self.reset_rect = self.ui.draw_ui(board_x + board_width + 20, board_y)
        
        # Draw algorithm visualization if enabled
        if self.show_algorithm:
            self.visualizer.draw_algorithm_visualization(
                self.WIDTH - self.VISUALIZATION_WIDTH, 0, 
                self.VISUALIZATION_WIDTH, self.HEIGHT,
                self.ai_engine.tree_nodes, 
                self.ai_engine.pruned_nodes,
                self.ai_engine.current_eval
            )

    def draw_board_contents(self, board_x, board_y):
        """Draw X's, O's and powerups on the board"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                center_x = board_x + col * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = board_y + row * self.CELL_SIZE + self.CELL_SIZE // 2
                
                # Highlight last move
                if self.last_move and (row, col) == self.last_move[:2]:
                    highlight_rect = pygame.Rect(
                        board_x + col * self.CELL_SIZE, board_y + row * self.CELL_SIZE,
                        self.CELL_SIZE, self.CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, self.colors['YELLOW'], highlight_rect, 3)
                
                # Draw powerups
                if self.board[row][col] == 0 and self.powerups[row][col] != 0:
                    self.draw_powerup(center_x, center_y, PowerUpType(self.powerups[row][col]))
                
                # Draw player marks
                if self.board[row][col] == 1:  # Player X
                    pygame.draw.line(self.screen, self.colors['BLUE'], 
                                    (center_x - 30, center_y - 30), 
                                    (center_x + 30, center_y + 30), 4)
                    pygame.draw.line(self.screen, self.colors['BLUE'], 
                                    (center_x + 30, center_y - 30), 
                                    (center_x - 30, center_y + 30), 4)
                elif self.board[row][col] == -1:  # AI O
                    pygame.draw.circle(self.screen, self.colors['RED'], 
                                    (center_x, center_y), 30, 4)
                elif self.board[row][col] == 2:  # Blocked cell
                    pygame.draw.line(self.screen, self.colors['BLACK'], 
                                   (center_x - 30, center_y - 30), 
                                   (center_x + 30, center_y + 30), 2)
                    pygame.draw.line(self.screen, self.colors['BLACK'], 
                                   (center_x + 30, center_y - 30), 
                                   (center_x - 30, center_y + 30), 2)
                    blocked_text = self.fonts['small'].render("BLOCKED", True, self.colors['BLACK'])
                    self.screen.blit(blocked_text, (center_x - 30, center_y + 10))

    def draw_powerup(self, center_x, center_y, power_type):
        """Draw a powerup on the board"""
        if power_type == PowerUpType.BLOCK:
            pygame.draw.rect(self.screen, self.colors['RED'], 
                           (center_x - 15, center_y - 15, 30, 30))
            power_label = self.fonts['small'].render("BLOCK", True, self.colors['WHITE'])
            self.screen.blit(power_label, (center_x - 20, center_y - 5))
        elif power_type == PowerUpType.SWAP:
            pygame.draw.rect(self.screen, self.colors['BLUE'], 
                           (center_x - 15, center_y - 15, 30, 30))
            power_label = self.fonts['small'].render("SWAP", True, self.colors['WHITE'])
            self.screen.blit(power_label, (center_x - 18, center_y - 5))
        elif power_type == PowerUpType.WILDCARD:
            pygame.draw.rect(self.screen, self.colors['YELLOW'], 
                           (center_x - 15, center_y - 15, 30, 30))
            power_label = self.fonts['small'].render("WILD", True, self.colors['BLACK'])
            self.screen.blit(power_label, (center_x - 15, center_y - 5))

    def draw_winning_line(self, board_x, board_y):
        """Draw winning line animation"""
        line_type, start, end = self.winning_line # type: ignore
        
        start_x = board_x + start[1] * self.CELL_SIZE + self.CELL_SIZE // 2
        start_y = board_y + start[0] * self.CELL_SIZE + self.CELL_SIZE // 2
        end_x = board_x + end[1] * self.CELL_SIZE + self.CELL_SIZE // 2
        end_y = board_y + end[0] * self.CELL_SIZE + self.CELL_SIZE // 2
        
        # Animate the line growing
        self.winning_line_animation = min(1.0, self.winning_line_animation + 0.05)
        current_end_x = start_x + (end_x - start_x) * self.winning_line_animation
        current_end_y = start_y + (end_y - start_y) * self.winning_line_animation
        
        # Determine color based on winner
        line_color = self.colors['BLUE'] if self.game_state == GameState.PLAYER_WIN else self.colors['RED']
        
        # Draw the line with glow effect
        line_width = 8
        pygame.draw.line(self.screen, line_color, (start_x, start_y), (current_end_x, current_end_y), line_width)
        
        # Glow effect
        glow_color = (
            min(255, line_color[0] + 50),
            min(255, line_color[1] + 50),
            min(255, line_color[2] + 50)
        )
        pygame.draw.line(self.screen, glow_color, (start_x, start_y), (current_end_x, current_end_y), line_width // 2)

    def handle_click(self, pos):
        """Handle mouse click events"""
        board_width = self.BOARD_SIZE * self.CELL_SIZE
        board_height = self.BOARD_SIZE * self.CELL_SIZE
        board_x = (self.WIDTH - self.VISUALIZATION_WIDTH - board_width) // 2
        board_y = (self.HEIGHT - board_height) // 2
        
        # Check if click is on UI elements
        ui_x = board_x + board_width + 20
        ui_y = board_y
        if self.ui.handle_ui_click(pos, ui_x, ui_y):
            return
        
        # If game is over or not player's turn, ignore board clicks
        if self.game_state != GameState.ONGOING or not self.player_turn:
            return
        
        # Check if click is within the board
        if (board_x <= pos[0] <= board_x + board_width and 
            board_y <= pos[1] <= board_y + board_height):
            col = (pos[0] - board_x) // self.CELL_SIZE
            row = (pos[1] - board_y) // self.CELL_SIZE
            
            if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
                self.handle_board_click(row, col)

    def handle_board_click(self, row, col):
        """Handle click on a board cell"""
        if self.selected_powerup and self.selected_powerup[0] == PowerUpType.SWAP:
            # Complete swap powerup action
            power_row, power_col = self.selected_powerup[1], self.selected_powerup[2]
            if self.board[row][col] != 0:  # Can only swap with occupied cell
                # Swap cells
                self.board[power_row][power_col], self.board[row][col] = \
                    self.board[row][col], self.board[power_row][power_col]
                self.selected_powerup = None
                self.last_move = (row, col, "SWAP")
                self.player_turn = False
                self.ai_thinking = True
        else:
            # Check if cell is empty
            if self.board[row][col] == 0:
                # Check if there's a powerup
                if self.powerups[row][col] != 0:
                    powerup_type = PowerUpType(self.powerups[row][col])
                    if powerup_type == PowerUpType.BLOCK:
                        self.use_block_powerup(row, col)
                    elif powerup_type == PowerUpType.SWAP:
                        self.use_swap_powerup(row, col)
                    elif powerup_type == PowerUpType.WILDCARD:
                        self.use_wildcard_powerup(row, col)
                    self.powerups[row][col] = 0
                else:
                    # Regular move
                    self.place_mark(row, col, 1)  # 1 represents player's mark (X)
                    
                    if self.check_winner() == 0:  # If game is not over
                        self.player_turn = False
                        self.ai_thinking = True

    def use_block_powerup(self, row, col):
        """Block a cell from AI use"""
        self.board[row][col] = 2  # Special value for blocked cell
        self.last_move = (row, col, "BLOCK")
        self.player_turn = False
        self.ai_thinking = True
    
    def use_swap_powerup(self, row, col):
        """Set the cell as "swap pending" and wait for another cell to be selected"""
        self.selected_powerup = (PowerUpType.SWAP, row, col)
        self.highlight_cells = [(row, col)]
    
    def use_wildcard_powerup(self, row, col):
        """Allow player to place their mark and get another turn"""
        self.place_mark(row, col, 1)
        self.last_move = (row, col, "WILD")
        # Player gets another turn, so don't switch to AI
    
    def place_mark(self, row, col, mark):
        """Place a mark on the board and check for game end"""
        self.board[row][col] = mark
        self.moves_history.append((row, col, mark))
        if not isinstance(self.last_move, tuple) or len(self.last_move) < 3 or self.last_move[2] != "WILD":
            self.last_move = (row, col, mark)
        
        # Check for win or draw
        result = self.check_winner()
        if result == 1:
            self.game_state = GameState.PLAYER_WIN
            self.find_winning_line(1)  # Player's mark
        elif result == -1:
            self.game_state = GameState.AI_WIN
            self.find_winning_line(-1)  # AI's mark
        elif result == 2:  # Draw
            self.game_state = GameState.DRAW

    def find_winning_line(self, mark):
        """Find the winning line for animation"""
        # Check rows
        for row in range(self.BOARD_SIZE):
            if all(self.board[row][col] == mark for col in range(self.BOARD_SIZE)):
                self.winning_line = ("row", (row, 0), (row, self.BOARD_SIZE-1))
                return
        
        # Check columns
        for col in range(self.BOARD_SIZE):
            if all(self.board[row][col] == mark for row in range(self.BOARD_SIZE)):
                self.winning_line = ("col", (0, col), (self.BOARD_SIZE-1, col))
                return
        
        # Check main diagonal
        if all(self.board[i][i] == mark for i in range(self.BOARD_SIZE)):
            self.winning_line = ("diag", (0, 0), (self.BOARD_SIZE-1, self.BOARD_SIZE-1))
            return
        
        # Check other diagonal
        if all(self.board[i][self.BOARD_SIZE-1-i] == mark for i in range(self.BOARD_SIZE)):
            self.winning_line = ("anti-diag", (0, self.BOARD_SIZE-1), (self.BOARD_SIZE-1, 0))
            return
        
        self.winning_line = None

    def check_winner(self):
        """Check if there's a winner or draw
        Return: 1 for player win, -1 for AI win, 2 for draw, 0 for ongoing
        """
        # Check rows
        for row in range(self.BOARD_SIZE):
            row_values = [val for val in self.board[row] if val != 2]  # Ignore blocked cells
            if len(row_values) == self.BOARD_SIZE and len(set(row_values)) == 1 and row_values[0] != 0:
                return row_values[0]
        
        # Check columns
        for col in range(self.BOARD_SIZE):
            col_values = [self.board[row][col] for row in range(self.BOARD_SIZE) if self.board[row][col] != 2]
            if len(col_values) == self.BOARD_SIZE and len(set(col_values)) == 1 and col_values[0] != 0:
                return col_values[0]
        
        # Check main diagonal
        diag_values = [self.board[i][i] for i in range(self.BOARD_SIZE) if self.board[i][i] != 2]
        if len(diag_values) == self.BOARD_SIZE and len(set(diag_values)) == 1 and diag_values[0] != 0:
            return diag_values[0]
        
        # Check other diagonal
        other_diag_values = [self.board[i][self.BOARD_SIZE-1-i] for i in range(self.BOARD_SIZE) 
                             if self.board[i][self.BOARD_SIZE-1-i] != 2]
        if len(other_diag_values) == self.BOARD_SIZE and len(set(other_diag_values)) == 1 and other_diag_values[0] != 0:
            return other_diag_values[0]
        
        # Check for draw (board full or no possible moves)
        if all(self.board[row][col] != 0 for row in range(self.BOARD_SIZE) for col in range(self.BOARD_SIZE)):
            return 2
        
        # Game ongoing
        return 0

    def get_valid_moves(self):
        """Get all valid moves on the board"""
        moves = []
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] == 0:
                    moves.append((row, col))
        return moves

    def ai_move(self):
        """Make the AI's move"""
        best_move = self.ai_engine.get_best_move(self.ai_personality)
        
        if best_move:
            self.place_mark(best_move[0], best_move[1], -1)  # -1 represents AI's mark (O)
        else:
            # No valid moves left - draw
            self.game_state = GameState.DRAW
        
        self.player_turn = True
        self.ai_thinking = False

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            
            # AI's turn
            if not self.player_turn and self.game_state == GameState.ONGOING:
                if self.ai_thinking:
                    # Show thinking animation first
                    self.draw_board()
                    pygame.display.flip()
                    time.sleep(0.5)  # Simulate thinking time
                    self.ai_move()
                else:
                    self.ai_thinking = True
            
            self.draw_board()
            pygame.display.flip()
            clock.tick(30)