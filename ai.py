import random
from enums import AIPersonality

class AIEngine:
    def __init__(self, game):
        self.game = game
        self.tree_nodes = []
        self.pruned_nodes = []
        self.current_eval = 0
        self.transposition_table = {}  # Cache for evaluated positions
    
    def reset(self):
        """Reset the AI engine's state"""
        self.tree_nodes = []
        self.pruned_nodes = []
        self.current_eval = 0
        self.transposition_table = {}
    
    def get_best_move(self, personality):
        """Get the best move based on AI personality"""
        self.reset()
        
        best_score = float('-inf')
        best_move = None
        
        valid_moves = self.game.get_valid_moves()
        
        if not valid_moves:
            return None
        
        # Random chance for non-optimal move based on personality
        if personality == AIPersonality.RANDOM and random.random() < 0.2:
            best_move = random.choice(valid_moves)
        else:
            # Optimization: First check for winning move
            winning_move = self.find_winning_move(valid_moves)
            if winning_move:
                return winning_move
                
            # Optimization: Then check for blocking move
            if personality != AIPersonality.AGGRESSIVE:
                blocking_move = self.find_blocking_move(valid_moves)
                if blocking_move:
                    return blocking_move
            
            # Standard minimax with alpha-beta pruning and transposition table
            alpha = float('-inf')
            beta = float('inf')
            
            for row, col in valid_moves:
                self.game.board[row][col] = -1  # AI mark
                
                # Deeper search for more advanced personalities
                max_depth = 5  # Simplified constant depth 
                if personality == AIPersonality.LEARNING:
                    max_depth += 1  # Deeper search for learning AI
                
                score = self.minimax_alpha_beta(0, max_depth, alpha, beta, False)
                self.game.board[row][col] = 0  # Undo move
                
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
                    
                alpha = max(alpha, best_score)
        
        self.current_eval = best_score if best_move else 0
        return best_move
    
    def find_winning_move(self, valid_moves):
        """Check if AI can win in one move"""
        for row, col in valid_moves:
            self.game.board[row][col] = -1  # AI mark
            if self.game.check_winner() == -1:  # AI wins
                self.game.board[row][col] = 0  # Undo move
                return (row, col)
            self.game.board[row][col] = 0  # Undo move
        return None
    
    def find_blocking_move(self, valid_moves):
        """Check if player can win in one move and block it"""
        for row, col in valid_moves:
            self.game.board[row][col] = 1  # Player mark
            if self.game.check_winner() == 1:  # Player would win
                self.game.board[row][col] = 0  # Undo move
                return (row, col)
            self.game.board[row][col] = 0  # Undo move
        return None
    
    def get_board_hash(self):
        """Generate a hash of the current board state for the transposition table"""
        return tuple(tuple(row) for row in self.game.board)
    
    def minimax_alpha_beta(self, depth, max_depth, alpha, beta, is_maximizing, node_id=0, parent_id=None):
        """Minimax algorithm with alpha-beta pruning and transposition table"""
        result = self.game.check_winner()
        
        # Terminal state evaluation
        if result != 0:
            value = 0
            if result == 1:  # Player wins
                value = -10 + depth  # Prefer longer paths to defeat
            elif result == -1:  # AI wins
                value = 10 - depth  # Prefer shorter paths to victory
            elif result == 2:  # Draw
                value = 0
            
            self.tree_nodes.append((depth, node_id, parent_id, value, False))
            return value
        
        if depth >= max_depth:  # Depth limit
            # Heuristic evaluation
            value = self.evaluate_board()
            self.tree_nodes.append((depth, node_id, parent_id, value, False))
            return value
        
        # Check transposition table
        board_hash = self.get_board_hash()
        if board_hash in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[board_hash]
            if stored_depth >= max_depth - depth:
                return stored_value
        
        next_node_id = len(self.tree_nodes) + 1
        
        if is_maximizing:  # AI's turn (maximizing)
            max_eval = float('-inf')
            moves = self.game.get_valid_moves()
            
            # Apply AI personality
            if self.game.ai_personality == AIPersonality.AGGRESSIVE:
                # Prioritize center and corners
                moves.sort(key=lambda m: 0 if (m[0] == m[1] == self.game.BOARD_SIZE//2 or 
                                             (m[0] in [0, self.game.BOARD_SIZE-1] and 
                                              m[1] in [0, self.game.BOARD_SIZE-1])) else 1)
            elif self.game.ai_personality == AIPersonality.DEFENSIVE:
                # Prioritize blocking player's potential wins
                moves.sort(key=lambda m: self.defensive_priority(m), reverse=True)
            elif self.game.ai_personality == AIPersonality.RANDOM and random.random() < 0.2:
                # 20% chance to randomize move order
                random.shuffle(moves)
            
            for i, (row, col) in enumerate(moves):
                child_id = next_node_id + i
                
                # Make move
                self.game.board[row][col] = -1
                
                # Recursive evaluation
                eval = self.minimax_alpha_beta(depth + 1, max_depth, alpha, beta, False, child_id, node_id)
                
                # Undo move
                self.game.board[row][col] = 0
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                
                # Pruning
                if beta <= alpha:
                    # Mark remaining moves as pruned
                    for j in range(i+1, len(moves)):
                        pruned_id = next_node_id + j
                        self.tree_nodes.append((depth + 1, pruned_id, node_id, None, True))
                        self.pruned_nodes.append(pruned_id)
                    break
            
            # Store in transposition table
            self.transposition_table[board_hash] = (max_depth - depth, max_eval)
            
            self.tree_nodes.append((depth, node_id, parent_id, max_eval, False))
            return max_eval
        
        else:  # Player's turn (minimizing)
            min_eval = float('inf')
            moves = self.game.get_valid_moves()
            
            for i, (row, col) in enumerate(moves):
                child_id = next_node_id + i
                
                # Make move
                self.game.board[row][col] = 1
                
                # Recursive evaluation
                eval = self.minimax_alpha_beta(depth + 1, max_depth, alpha, beta, True, child_id, node_id)
                
                # Undo move
                self.game.board[row][col] = 0
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                
                # Pruning
                if beta <= alpha:
                    # Mark remaining moves as pruned
                    for j in range(i+1, len(moves)):
                        pruned_id = next_node_id + j
                        self.tree_nodes.append((depth + 1, pruned_id, node_id, None, True))
                        self.pruned_nodes.append(pruned_id)
                    break
            
            # Store in transposition table
            self.transposition_table[board_hash] = (max_depth - depth, min_eval)
            
            self.tree_nodes.append((depth, node_id, parent_id, min_eval, False))
            return min_eval
    
    def evaluate_board(self):
        """Improved heuristic evaluation for non-terminal states"""
        score = 0
        
        # Evaluate rows, columns, and diagonals
        lines = []
        
        # Rows
        for row in range(self.game.BOARD_SIZE):
            lines.append([self.game.board[row][col] for col in range(self.game.BOARD_SIZE)])
        
        # Columns
        for col in range(self.game.BOARD_SIZE):
            lines.append([self.game.board[row][col] for row in range(self.game.BOARD_SIZE)])
        
        # Diagonals
        lines.append([self.game.board[i][i] for i in range(self.game.BOARD_SIZE)])
        lines.append([self.game.board[i][self.game.BOARD_SIZE-1-i] for i in range(self.game.BOARD_SIZE)])
        
        # Evaluate each line
        for line in lines:
            score += self.evaluate_line(line)
        
        # Add bonus for center control (important in tic-tac-toe)
        center = self.game.BOARD_SIZE // 2
        if self.game.board[center][center] == -1:  # AI has center
            score += 2
        elif self.game.board[center][center] == 1:  # Player has center
            score -= 2
            
        return score
    
    def evaluate_line(self, line):
        """Evaluate a single line (row, column, or diagonal)"""
        # Count AI marks, player marks, and empty cells
        ai_count = line.count(-1)
        player_count = line.count(1)
        empty_count = line.count(0)
        
        # Blocked cells don't contribute to winning
        if 2 in line:
            return 0
        
        # Score based on potential to win
        if player_count == 0 and ai_count > 0:
            return ai_count * ai_count  # Square for emphasis on near-wins
        elif ai_count == 0 and player_count > 0:
            return -player_count * player_count
        
        return 0
    
    def defensive_priority(self, move):
        """Calculate defensive priority for a move"""
        row, col = move
        self.game.board[row][col] = 1  # Temporarily place player mark
        
        # Check if this would block a potential win
        for i in range(self.game.BOARD_SIZE):
            # Check row
            if sum(self.game.board[row]) == self.game.BOARD_SIZE - 1:
                self.game.board[row][col] = 0
                return 10
            
            # Check column
            col_sum = sum(self.game.board[j][col] for j in range(self.game.BOARD_SIZE))
            if col_sum == self.game.BOARD_SIZE - 1:
                self.game.board[row][col] = 0
                return 10
        
        # Check diagonals if applicable
        if row == col:  # On main diagonal
            diag_sum = sum(self.game.board[i][i] for i in range(self.game.BOARD_SIZE))
            if diag_sum == self.game.BOARD_SIZE - 1:
                self.game.board[row][col] = 0
                return 10
        
        if row + col == self.game.BOARD_SIZE - 1:  # On other diagonal
            other_diag_sum = sum(self.game.board[i][self.game.BOARD_SIZE-1-i] for i in range(self.game.BOARD_SIZE))
            if other_diag_sum == self.game.BOARD_SIZE - 1:
                self.game.board[row][col] = 0
                return 10
        
        # Restore the board
        self.game.board[row][col] = 0
        return 0