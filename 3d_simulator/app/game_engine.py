"""
Game engine for the 3D language simulator.
"""

import pygame
from .board import Board
from .simulator import Simulator
from .ui import UI

class GameEngine:
    def __init__(self):
        self.board = Board()
        self.ui = UI()
        self.running = True
        self.auto_run = False
        self.auto_run_delay = 500  # milliseconds
        self.last_auto_step = 0
        
        # Load a simple example first
        self._load_example()
        
        # Then initialize simulator with the loaded board
        self.simulator = Simulator(self.board, 42, 7)
    
    def _load_example(self):
        """Load a simple example program: Simple movement without time warp"""
        print("Loading example program...")  # Debug log
        
        # Simple example: A moves right to S
        self.board.set_cell(0, 5, 'A')  # Input A (will become 42)
        self.board.set_cell(1, 5, '>')  # Move right
        self.board.set_cell(2, 5, '>')  # Move right
        self.board.set_cell(3, 5, 'S')  # Output
        
        print("Example program loaded:")  # Debug log
        for x, y, value in self.board.get_all_cells():
            print(f"  ({x}, {y}): {value}")
    
    def _load_time_warp_example(self):
        """Load a time warp example program"""
        print("Loading time warp example program...")  # Debug log
        
        # ICFP 2024 time warp example:
        # 2 > . .
        # . 2 @ 0  
        # . . 1 .
        # This should result in: 2 > 2 . after time warp
        self.board.set_cell(0, 4, 2)   # Value to move
        self.board.set_cell(1, 4, '>')  # Move right
        self.board.set_cell(1, 5, 2)   # dx (will be consumed)
        self.board.set_cell(2, 5, '@')  # Time warp operator
        self.board.set_cell(3, 5, 0)   # dy (will be consumed)
        self.board.set_cell(2, 6, 1)   # dt (will be consumed)
        # Note: v will be the value that moves to (2,4) in step 1
        
        print("Time warp example program loaded:")  # Debug log
        for x, y, value in self.board.get_all_cells():
            print(f"  ({x}, {y}): {value}")
    
    def load_time_warp_test(self):
        """Public method to load time warp test"""
        self.board.clear()
        self._load_time_warp_example()
        self.simulator = Simulator(self.board, 42, 7)
    
    def run(self):
        """Main game loop."""
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            events = self.ui.handle_events(self)
            for event in events:
                self._handle_event(event)
            
            # Auto-run logic
            if (self.auto_run and self.simulator.running and 
                current_time - self.last_auto_step > self.auto_run_delay):
                self.simulator.step()
                self.last_auto_step = current_time
            
            # Render
            self.ui.render(self)
        
        pygame.quit()
    
    def _handle_event(self, event):
        """Handle game events."""
        print(f"Handling event: {event}")  # Debug log
        
        if event[0] == 'quit':
            self.running = False
        
        elif event[0] == 'button':
            button_name = event[1]
            print(f"Button pressed: {button_name}")  # Debug log
            
            if button_name == 'step':
                print(f"Step button - simulator running: {self.simulator.running}")  # Debug log
                print(f"Current tick: {self.simulator.tick}")  # Debug log
                print(f"Board cells: {len(self.board.get_all_cells())}")  # Debug log
                
                if not self.simulator.running:
                    self.simulator.start()
                    print("Simulator started")  # Debug log
                
                result = self.simulator.step()
                print(f"Step result: {result}")  # Debug log
                print(f"New tick: {self.simulator.tick}")  # Debug log
                self.auto_run = False
            
            elif button_name == 'reset':
                print("Reset button pressed")  # Debug log
                print(f"Before reset - board has {len(self.board.get_all_cells())} cells")  # Debug log
                
                # Reload the example program
                self.board.clear()
                self._load_example()
                
                # Reinitialize simulator with fresh board
                self.simulator = Simulator(self.board, 42, 7)
                self.auto_run = False
                
                print(f"After reset - board has {len(self.board.get_all_cells())} cells")  # Debug log
            
            elif button_name == 'start':
                if self.simulator.running:
                    self.simulator.stop()
                    self.auto_run = False
                    print("Simulation stopped")  # Debug log
                else:
                    self.simulator.start()
                    self.auto_run = True
                    self.last_auto_step = pygame.time.get_ticks()
                    print("Simulation started")  # Debug log
    
    def set_input_a(self, value):
        """Set input A value."""
        try:
            val = int(value)
            self.simulator.set_inputs(val, self.simulator.input_b)
        except ValueError:
            pass
    
    def set_input_b(self, value):
        """Set input B value."""
        try:
            val = int(value)
            self.simulator.set_inputs(self.simulator.input_a, val)
        except ValueError:
            pass
