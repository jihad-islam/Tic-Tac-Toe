import pygame
from enums import AIPersonality, GameState

class GameUI:
    def __init__(self, game, screen, colors, fonts):
        """Initialize the UI component"""
        self.game = game
        self.screen = screen
        self.colors = colors
        self.fonts = fonts
        self.play_again_rect = None
    
    def draw_ui(self, x, y):
        """Draw the game UI elements"""
        # Draw game status with enhanced visibility
        status_text, status_color = self.get_status_text_and_color()
        status_rect = pygame.Rect(x, y, 180, 40)
        pygame.draw.rect(self.screen, self.colors['GRAY'], status_rect)
        status_surface = self.fonts['normal'].render(status_text, True, status_color)
        self.screen.blit(status_surface, (x + 10, y + 8))
        
        # Draw "Play Again" button when game is over
        if self.game.game_state != GameState.ONGOING:
            play_again_rect = pygame.Rect(x, y + 50, 180, 40)
            pygame.draw.rect(self.screen, self.colors['GREEN'], play_again_rect)
            play_again_text = self.fonts['normal'].render("Play Again", True, self.colors['BLACK'])
            self.screen.blit(play_again_text, (x + 40, y + 58))
            
            # Store play again rect and return it
            self.play_again_rect = play_again_rect
            return play_again_rect
        
        # Draw AI personality selector with title
        personality_y = y + 60  # Moved up since there's no board size selector
        personality_text = self.fonts['normal'].render("AI Personality:", True, self.colors['BLACK'])
        self.screen.blit(personality_text, (x, personality_y))
        
        for i, personality in enumerate(AIPersonality):
            rect = pygame.Rect(x, personality_y + 30 + i*35, 180, 30)
            color = self.colors['GREEN'] if self.game.ai_personality == personality else self.colors['GRAY']
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors['BLACK'], rect, 2)  # Border
            p_text = self.fonts['normal'].render(personality.name, True, self.colors['BLACK'])
            self.screen.blit(p_text, (x + 10, personality_y + 35 + i*35))
        
        # Draw algorithm visualization toggle
        vis_y = personality_y + 210
        vis_text = self.fonts['normal'].render("Algorithm Visualization:", True, self.colors['BLACK'])
        self.screen.blit(vis_text, (x, vis_y))
        
        vis_rect = pygame.Rect(x, vis_y + 30, 180, 30)
        vis_color = self.colors['GREEN'] if self.game.show_algorithm else self.colors['GRAY']
        pygame.draw.rect(self.screen, vis_color, vis_rect)
        pygame.draw.rect(self.screen, self.colors['BLACK'], vis_rect, 2)  # Border
        toggle_text = self.fonts['normal'].render("ON" if self.game.show_algorithm else "OFF", True, self.colors['BLACK'])
        self.screen.blit(toggle_text, (x + 80, vis_y + 35))
        
        # Draw reset button with better styling
        reset_rect = pygame.Rect(x, vis_y + 80, 180, 40)
        pygame.draw.rect(self.screen, self.colors['RED'], reset_rect)
        pygame.draw.rect(self.screen, self.colors['BLACK'], reset_rect, 2)  # Border
        reset_text = self.fonts['normal'].render("Reset Game", True, self.colors['WHITE'])
        self.screen.blit(reset_text, (x + 40, vis_y + 90))
        
        # Reset play_again_rect when game is ongoing
        self.play_again_rect = None
        return reset_rect
    
    def get_status_text_and_color(self):
        """Get game status text and color"""
        if self.game.game_state == GameState.PLAYER_WIN:
            return "You Win!", self.colors['GREEN']
        elif self.game.game_state == GameState.AI_WIN:
            return "AI Wins!", self.colors['RED']
        elif self.game.game_state == GameState.DRAW:
            return "It's a Draw!", self.colors['BLUE']
        else:
            return "Your Turn" if self.game.player_turn else "AI Thinking...", self.colors['BLACK']
    
    def handle_ui_click(self, pos, ui_x, ui_y):
        """Handle clicks on UI elements"""
        # Play Again button (only visible when game is over)
        if self.play_again_rect and self.play_again_rect.collidepoint(pos):
            self.game.reset_game()
            return True
        
        # If game is over, only the Play Again button should be clickable
        if self.game.game_state != GameState.ONGOING:
            return False
        
        # AI personality buttons
        personality_y = ui_y + 60  # Updated to match new position
        for i, personality in enumerate(AIPersonality):
            rect = pygame.Rect(ui_x, personality_y + 30 + i*35, 180, 30)
            if rect.collidepoint(pos):
                self.game.ai_personality = personality
                return True
        
        # Algorithm visualization toggle
        vis_y = personality_y + 210
        vis_rect = pygame.Rect(ui_x, vis_y + 30, 180, 30)
        if vis_rect.collidepoint(pos):
            self.game.show_algorithm = not self.game.show_algorithm
            return True
        
        # Reset button
        reset_rect = pygame.Rect(ui_x, vis_y + 80, 180, 40)
        if reset_rect.collidepoint(pos):
            self.game.reset_game()
            return True
        
        return False