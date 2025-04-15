import pygame

class AlgorithmVisualizer:
    def __init__(self, screen, colors, fonts):
        """Initialize the visualization component"""
        self.screen = screen
        self.colors = colors
        self.fonts = fonts
    
    def draw_algorithm_visualization(self, x, y, width, height, tree_nodes, pruned_nodes, current_eval):
        """Draw the algorithm visualization panel"""
        # Draw background panel with gradient effect
        pygame.draw.rect(self.screen, self.colors['GRAY'], (x, y, width, height))
        pygame.draw.rect(self.screen, self.colors['BLACK'], (x, y, width, height), 2)
        
        # Title with better styling
        panel_title = self.fonts['normal'].render("Algorithm Visualization", True, self.colors['BLACK'])
        title_bg = pygame.Rect(x, y, width, 40)
        pygame.draw.rect(self.screen, self.colors['LIGHT_BLUE'], title_bg)
        pygame.draw.rect(self.screen, self.colors['BLACK'], title_bg, 2)
        self.screen.blit(panel_title, (x + (width - panel_title.get_width()) // 2, y + 10))
        
        # Draw evaluation gauge
        gauge_y = y + 60
        pygame.draw.rect(self.screen, self.colors['WHITE'], (x + 20, gauge_y, width - 40, 30))
        pygame.draw.rect(self.screen, self.colors['BLACK'], (x + 20, gauge_y, width - 40, 30), 2)
        
        # Gauge center line
        center_x = x + 20 + (width - 40) // 2
        pygame.draw.line(self.screen, self.colors['BLACK'], 
                         (center_x, gauge_y), (center_x, gauge_y + 30), 2)
        
        # Current evaluation marker
        eval_range = 20  # Scale factor
        marker_x = x + 20 + (width - 40) // 2 + int(current_eval * (width - 40) / (2 * eval_range))
        marker_x = max(x + 20, min(x + width - 20, marker_x))
        
        # Draw a more visible marker
        pygame.draw.circle(self.screen, self.colors['RED'], (marker_x, gauge_y + 15), 10)
        pygame.draw.circle(self.screen, self.colors['BLACK'], (marker_x, gauge_y + 15), 10, 2)
        
        # Fill gauge based on evaluation
        if current_eval > 0:  # AI advantage
            advantage_width = int(current_eval * (width - 40) / (2 * eval_range))
            advantage_width = min(advantage_width, (width - 40) // 2)
            pygame.draw.rect(self.screen, (255, 200, 200), 
                           (center_x, gauge_y + 1, advantage_width, 28))
        elif current_eval < 0:  # Player advantage
            advantage_width = int(-current_eval * (width - 40) / (2 * eval_range))
            advantage_width = min(advantage_width, (width - 40) // 2)
            pygame.draw.rect(self.screen, (200, 200, 255), 
                           (center_x - advantage_width, gauge_y + 1, advantage_width, 28))
        
        # Draw labels with better positioning
        ai_win = self.fonts['normal'].render("AI Win", True, self.colors['RED'])
        player_win = self.fonts['normal'].render("Player Win", True, self.colors['BLUE'])
        self.screen.blit(ai_win, (x + width - 100, gauge_y + 5))
        self.screen.blit(player_win, (x + 30, gauge_y + 5))
        
        # Draw current evaluation text
        eval_text = self.fonts['normal'].render(f"Eval: {current_eval:.1f}", True, self.colors['BLACK'])
        self.screen.blit(eval_text, (x + (width - eval_text.get_width()) // 2, gauge_y + 40))
        
        # Draw search tree stats with styled background
        tree_start_y = gauge_y + 80
        stats_bg = pygame.Rect(x + 10, tree_start_y, width - 20, 70)
        pygame.draw.rect(self.screen, self.colors['LIGHT_GREEN'], stats_bg)
        pygame.draw.rect(self.screen, self.colors['BLACK'], stats_bg, 2)
        
        # Default to 0 when no nodes
        node_count = len(tree_nodes) if tree_nodes else 0
        pruned_count = len(pruned_nodes) if pruned_nodes else 0
        
        nodes_text = self.fonts['normal'].render(f"Nodes explored: {node_count}", True, self.colors['BLACK'])
        pruned_text = self.fonts['normal'].render(f"Nodes pruned: {pruned_count}", True, self.colors['BLACK'])
        self.screen.blit(nodes_text, (x + 20, tree_start_y + 10))
        self.screen.blit(pruned_text, (x + 20, tree_start_y + 40))
        
        # Draw a simple tree representation if we have nodes
        if tree_nodes:
            tree_title = self.fonts['normal'].render("Decision Tree", True, self.colors['BLACK'])
            self.screen.blit(tree_title, (x + (width - tree_title.get_width()) // 2, tree_start_y + 90))
            
            tree_height = height - tree_start_y - 130
            tree_width = width - 40
            
            max_depth = max([node[0] for node in tree_nodes]) if tree_nodes else 0
            if max_depth > 0:
                level_height = tree_height / (max_depth + 1)
                
                # Draw connecting lines first
                for i, (depth, node_id, parent_id, value, pruned) in enumerate(tree_nodes):
                    if parent_id is not None:
                        # Find parent coordinates
                        parent_x, parent_y = None, None
                        for d, nid, pid, v, p in tree_nodes:
                            if nid == parent_id:
                                parent_y = tree_start_y + 120 + d * level_height
                                parent_x = x + 20 + (tree_width * nid) / (2**(d+1))
                                break
                        
                        if parent_x is not None:
                            node_y = tree_start_y + 120 + depth * level_height
                            node_x = x + 20 + (tree_width * node_id) / (2**(depth+1))
                            line_color = self.colors['RED'] if pruned else self.colors['BLACK']
                            pygame.draw.line(self.screen, line_color, 
                                            (parent_x, parent_y), 
                                            (node_x, node_y), 2)
                
                # Draw nodes
                for depth, node_id, parent_id, value, pruned in tree_nodes:
                    node_y = tree_start_y + 120 + depth * level_height
                    # Position horizontally based on binary tree layout
                    node_x = x + 20 + (tree_width * node_id) / (2**(depth+1))
                    
                    # Node circle with border
                    node_color = self.colors['RED'] if pruned else self.colors['BLUE']
                    pygame.draw.circle(self.screen, node_color, (int(node_x), int(node_y)), 10)
                    pygame.draw.circle(self.screen, self.colors['BLACK'], (int(node_x), int(node_y)), 10, 2)
                    
                    # Value text with background for better visibility
                    if value is not None:
                        value_text = self.fonts['small'].render(f"{value:.1f}", True, self.colors['BLACK'])
                        text_bg_rect = pygame.Rect(
                            node_x - 15, node_y + 15, 
                            value_text.get_width() + 6, value_text.get_height() + 2
                        )
                        pygame.draw.rect(self.screen, self.colors['WHITE'], text_bg_rect)
                        pygame.draw.rect(self.screen, self.colors['BLACK'], text_bg_rect, 1)
                        self.screen.blit(value_text, (node_x - 12, node_y + 16))