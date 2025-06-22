"""
UI class for the 3D language simulator using pygame.
"""

import pygame
import sys

class UI:
    def __init__(self, screen_width=1000, screen_height=700):
        pygame.init()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("3D Language Simulator")
        
        # Colors
        self.colors = {
            'background': (240, 240, 240),
            'grid_line': (200, 200, 200),
            'cell_empty': (255, 255, 255),
            'cell_number': (200, 230, 255),
            'cell_operator': (255, 200, 200),
            'cell_input': (200, 255, 200),
            'cell_output': (255, 255, 150),
            'cell_selected': (150, 150, 255),
            'text': (0, 0, 0),
            'button': (220, 220, 220),
            'button_hover': (200, 200, 200)
        }
        
        # Layout
        self.control_panel_height = 60
        self.status_panel_height = 40
        self.grid_area_y = self.control_panel_height
        self.grid_area_height = screen_height - self.control_panel_height - self.status_panel_height
        
        # Grid settings
        self.cell_size = 40
        self.grid_offset_x = 50
        self.grid_offset_y = self.grid_area_y + 20
        
        # Fonts
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        
        # UI state
        self.selected_cell = None
        self.input_mode = False
        self.input_text = ""
        
        # Buttons
        self.buttons = {
            'step': pygame.Rect(10, 10, 60, 40),
            'reset': pygame.Rect(80, 10, 60, 40),
            'start': pygame.Rect(150, 10, 60, 40)
        }
        
        self.input_boxes = {
            'input_a': pygame.Rect(250, 15, 50, 30),
            'input_b': pygame.Rect(350, 15, 50, 30)
        }
        
        self.clock = pygame.time.Clock()
    
    def handle_events(self, game_engine):
        """Handle pygame events."""
        events = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(('quit',))
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    
                    # Check button clicks
                    for button_name, rect in self.buttons.items():
                        if rect.collidepoint(mouse_x, mouse_y):
                            print(f"Button clicked: {button_name}")  # Debug log
                            events.append(('button', button_name))
                            break
                    else:
                        # Check grid clicks
                        grid_x, grid_y = self._screen_to_grid(mouse_x, mouse_y)
                        if grid_x is not None and grid_y is not None:
                            print(f"Cell clicked: ({grid_x}, {grid_y})")  # Debug log
                            self.selected_cell = (grid_x, grid_y)
                            self.input_mode = True
                            self.input_text = ""
                            
                            # Get current cell value
                            current_value = game_engine.board.get_cell(grid_x, grid_y)
                            print(f"Current cell value: {current_value}")  # Debug log
                            if current_value is not None:
                                self.input_text = str(current_value)
            
            elif event.type == pygame.KEYDOWN:
                if self.input_mode and self.selected_cell:
                    print(f"Key pressed in input mode: {event.key}, char: '{event.unicode}'")  # Debug log
                    if event.key == pygame.K_RETURN:
                        print("Enter key - committing input")  # Debug log
                        # Commit input
                        self._commit_cell_input(game_engine)
                    elif event.key == pygame.K_ESCAPE:
                        print("Escape key - canceling input")  # Debug log
                        # Cancel input
                        self.input_mode = False
                        self.selected_cell = None
                        self.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                        print(f"Backspace - input text now: '{self.input_text}'")  # Debug log
                    elif event.key == pygame.K_DELETE:
                        self.input_text = ""
                        print("Delete - input text cleared")  # Debug log
                    else:
                        # Add character to input
                        char = event.unicode
                        if char and len(self.input_text) < 10:
                            self.input_text += char
                            print(f"Added char '{char}' - input text now: '{self.input_text}'")  # Debug log
                else:
                    # Global hotkeys
                    print(f"Key pressed: {event.key}")  # Debug log
                    if event.key == pygame.K_SPACE:
                        print("Space key detected!")  # Debug log
                        events.append(('button', 'step'))
                    elif event.key == pygame.K_r:
                        print("R key detected!")  # Debug log
                        events.append(('button', 'reset'))
                    elif event.key == pygame.K_s:
                        print("S key detected!")  # Debug log
                        events.append(('button', 'start'))
        
        return events
    
    def _screen_to_grid(self, screen_x, screen_y):
        """Convert screen coordinates to grid coordinates."""
        if (screen_y < self.grid_offset_y or 
            screen_x < self.grid_offset_x):
            return None, None
        
        grid_x = (screen_x - self.grid_offset_x) // self.cell_size
        grid_y = (screen_y - self.grid_offset_y) // self.cell_size
        
        # Limit to reasonable bounds
        if 0 <= grid_x < 25 and 0 <= grid_y < 15:
            return grid_x, grid_y
        
        return None, None
    
    def _grid_to_screen(self, grid_x, grid_y):
        """Convert grid coordinates to screen coordinates."""
        screen_x = self.grid_offset_x + grid_x * self.cell_size
        screen_y = self.grid_offset_y + grid_y * self.cell_size
        return screen_x, screen_y
    
    def _commit_cell_input(self, game_engine):
        """Commit the current input to the selected cell."""
        if not self.selected_cell:
            print("No selected cell to commit")  # Debug log
            return
        
        grid_x, grid_y = self.selected_cell
        text = self.input_text.strip()
        print(f"Committing input '{text}' to cell ({grid_x}, {grid_y})")  # Debug log
        
        if text == "" or text == ".":
            # Empty cell
            print("Setting cell to empty")  # Debug log
            game_engine.board.set_cell(grid_x, grid_y, None)
        else:
            # Try to parse as integer
            try:
                value = int(text)
                if -99 <= value <= 99:
                    print(f"Setting cell to integer: {value}")  # Debug log
                    game_engine.board.set_cell(grid_x, grid_y, value)
                else:
                    print(f"Invalid integer range: {value}")  # Debug log
                    return  # Invalid range
            except ValueError:
                # Must be an operator
                if game_engine.board.is_valid_token(text):
                    print(f"Setting cell to operator: {text}")  # Debug log
                    game_engine.board.set_cell(grid_x, grid_y, text)
                else:
                    print(f"Invalid token: {text}")  # Debug log
                    return  # Invalid token
        
        # Reset simulation when board changes
        # Update the initial board to reflect the changes
        game_engine.simulator.initial_board = game_engine.board.copy()
        game_engine.simulator.tick = 1
        game_engine.simulator.history = [game_engine.board.copy()]
        game_engine.simulator.running = False
        game_engine.simulator.submitted_value = None
        
        print(f"Board updated - now has {len(game_engine.board.get_all_cells())} cells")  # Debug log
        
        # Reset UI state
        self.input_mode = False
        self.selected_cell = None
        self.input_text = ""
        self.input_text = ""
    
    def render(self, game_engine):
        """Render the entire UI."""
        self.screen.fill(self.colors['background'])
        
        self._draw_control_panel(game_engine)
        self._draw_grid(game_engine)
        self._draw_status_panel(game_engine)
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def _draw_control_panel(self, game_engine):
        """Draw the control panel at the top."""
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        
        for button_name, rect in self.buttons.items():
            color = self.colors['button_hover'] if rect.collidepoint(mouse_pos) else self.colors['button']
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors['text'], rect, 2)
            
            # Button text
            text = button_name.capitalize()
            if button_name == 'start':
                text = 'Start' if not game_engine.simulator.running else 'Stop'
            
            text_surface = self.font_medium.render(text, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Input boxes
        a_text = f"A: {game_engine.simulator.input_a}"
        b_text = f"B: {game_engine.simulator.input_b}"
        tick_text = f"T: {game_engine.simulator.tick:03d}"
        
        a_surface = self.font_medium.render(a_text, True, self.colors['text'])
        b_surface = self.font_medium.render(b_text, True, self.colors['text'])
        tick_surface = self.font_medium.render(tick_text, True, self.colors['text'])
        
        self.screen.blit(a_surface, (250, 20))
        self.screen.blit(b_surface, (350, 20))
        self.screen.blit(tick_surface, (450, 20))
        
        # Submitted value
        if game_engine.simulator.submitted_value is not None:
            result_text = f"Result: {game_engine.simulator.submitted_value}"
            result_surface = self.font_medium.render(result_text, True, (0, 150, 0))
            self.screen.blit(result_surface, (550, 20))
    
    def _draw_grid(self, game_engine):
        """Draw the main grid."""
        # Draw grid lines
        for x in range(26):  # 0 to 25
            screen_x = self.grid_offset_x + x * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid_line'], 
                           (screen_x, self.grid_offset_y), 
                           (screen_x, self.grid_offset_y + 15 * self.cell_size))
        
        for y in range(16):  # 0 to 15
            screen_y = self.grid_offset_y + y * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid_line'], 
                           (self.grid_offset_x, screen_y), 
                           (self.grid_offset_x + 25 * self.cell_size, screen_y))
        
        # Draw cells
        for x in range(25):
            for y in range(15):
                self._draw_cell(game_engine, x, y)
    
    def _draw_cell(self, game_engine, grid_x, grid_y):
        """Draw a single cell."""
        screen_x, screen_y = self._grid_to_screen(grid_x, grid_y)
        cell_rect = pygame.Rect(screen_x + 1, screen_y + 1, 
                               self.cell_size - 2, self.cell_size - 2)
        
        value = game_engine.board.get_cell(grid_x, grid_y)
        
        # Determine cell color
        if (grid_x, grid_y) == self.selected_cell:
            color = self.colors['cell_selected']
        elif value is None:
            color = self.colors['cell_empty']
        elif isinstance(value, int):
            color = self.colors['cell_number']
        elif value in ['A', 'B']:
            color = self.colors['cell_input']
        elif value == 'S':
            color = self.colors['cell_output']
        else:
            color = self.colors['cell_operator']
        
        pygame.draw.rect(self.screen, color, cell_rect)
        
        # Draw cell content
        text_to_show = None
        
        if self.input_mode and (grid_x, grid_y) == self.selected_cell:
            # Show input text with cursor
            text_to_show = self.input_text + "|"
        elif value is not None:
            # Show actual cell value
            text_to_show = str(value)
        
        if text_to_show:
            text_surface = self.font_medium.render(text_to_show, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=cell_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_status_panel(self, game_engine):
        """Draw the status panel at the bottom."""
        status_y = self.screen_height - self.status_panel_height
        
        # Background
        status_rect = pygame.Rect(0, status_y, self.screen_width, self.status_panel_height)
        pygame.draw.rect(self.screen, (250, 250, 250), status_rect)
        pygame.draw.line(self.screen, self.colors['grid_line'], 
                        (0, status_y), (self.screen_width, status_y))
        
        # Status text
        if game_engine.simulator.submitted_value is not None:
            status = f"Submitted: {game_engine.simulator.submitted_value}"
        elif game_engine.simulator.running:
            status = "Running..."
        else:
            status = "Ready"
        
        # Spacetime volume
        volume = game_engine.simulator.get_spacetime_volume()
        volume_text = f"Volume: {volume}"
        
        status_surface = self.font_medium.render(status, True, self.colors['text'])
        volume_surface = self.font_medium.render(volume_text, True, self.colors['text'])
        
        self.screen.blit(status_surface, (10, status_y + 10))
        self.screen.blit(volume_surface, (200, status_y + 10))
        
        # Instructions
        if self.input_mode:
            instruction = "Enter value, press Enter to confirm, Esc to cancel"
        else:
            instruction = "Click cell to edit, Space=Step, R=Reset, S=Start/Stop"
        
        instruction_surface = self.font_small.render(instruction, True, self.colors['text'])
        self.screen.blit(instruction_surface, (400, status_y + 15))
