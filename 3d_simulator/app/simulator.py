"""
Simulator class for executing 3D language programs.
"""

from .board import Board
from .operators import OperatorProcessor

class Simulator:
    def __init__(self, board, input_a=0, input_b=0):
        print(f"Initializing simulator with board containing {len(board.get_all_cells())} cells")  # Debug log
        
        self.input_a = input_a
        self.input_b = input_b
        
        # Work with the same board object, not a copy
        self.board = board
        self.tick = 1
        self.running = False
        self.submitted_value = None
        self.max_ticks = 1000000
        
        # Store initial board WITHOUT replacing A, B
        self.initial_board = self.board.copy()
        self.history = [self.board.copy()]
        
        print(f"Simulator initialized with {len(self.board.get_all_cells())} cells")  # Debug log
    
    def _replace_inputs(self):
        """Replace A and B tokens with actual input values."""
        print(f"Replacing inputs: A={self.input_a}, B={self.input_b}")  # Debug log
        replaced_count = 0
        for x, y, value in self.board.get_all_cells():
            if value == 'A':
                print(f"Replacing A at ({x}, {y}) with {self.input_a}")  # Debug log
                self.board.set_cell(x, y, self.input_a)
                replaced_count += 1
            elif value == 'B':
                print(f"Replacing B at ({x}, {y}) with {self.input_b}")  # Debug log
                self.board.set_cell(x, y, self.input_b)
                replaced_count += 1
        print(f"Replaced {replaced_count} input tokens")  # Debug log
    
    def step(self):
        """Execute one tick of the simulation."""
        print(f"Step called - tick: {self.tick}, running: {self.running}, submitted: {self.submitted_value}")  # Debug log
        
        if not self.running or self.submitted_value is not None:
            print("Step aborted - not running or already submitted")  # Debug log
            return False
        
        if self.tick >= self.max_ticks:
            print("Step aborted - max ticks reached")  # Debug log
            self.running = False
            return False
        
        print(f"Processing operators at tick {self.tick}")  # Debug log
        
        # Debug: Show current board state
        print("Current board state:")
        for x, y, value in self.board.get_all_cells():
            print(f"  ({x}, {y}): {value}")
        
        processor = OperatorProcessor(self.board)
        
        try:
            time_warps = processor.process_all_operators()
            print(f"Operators processed - writes: {len(processor.pending_writes)}, removes: {len(processor.pending_removes)}")  # Debug log
            
            # Check for submission
            if self._check_submission():
                print("Submission detected!")  # Debug log
                self.running = False
                return False
            
            # Handle time warps
            if time_warps:
                print(f"Time warp detected: {time_warps[0]}")  # Debug log
                self._handle_time_warp(time_warps[0])
            else:
                # Normal progression
                self.tick += 1
                self.history.append(self.board.copy())
                print(f"Advanced to tick {self.tick}")  # Debug log
            
            # Check if no operators can reduce (deadlock)
            if not self._has_reducible_operators():
                print("No reducible operators - stopping")  # Debug log
                self.running = False
                return False
                
        except RuntimeError as e:
            print(f"Simulation error: {e}")
            self.running = False
            return False
        
        return True
    
    def _check_submission(self):
        """Check if any S operator has been overwritten."""
        submitted_values = []
        
        # Check all positions that had S in the original board (before A,B replacement)
        for x, y, value in self.initial_board.get_all_cells():
            if value == 'S':
                # Check what's at this position now
                current_value = self.board.get_cell(x, y)
                if current_value != 'S':
                    # S has been overwritten
                    print(f"S at ({x}, {y}) overwritten with {current_value}")  # Debug log
                    submitted_values.append(current_value)
        
        if submitted_values:
            # Check for multiple different submissions
            unique_values = set(submitted_values)
            if len(unique_values) > 1:
                raise RuntimeError(f"Multiple different values submitted: {unique_values}")
            
            self.submitted_value = submitted_values[0]
            print(f"Submitted value: {self.submitted_value}")  # Debug log
            return True
        
        return False
    
    def _handle_time_warp(self, time_warp):
        """Handle time warp operation."""
        at_x, at_y, dx, dy, dt, value = time_warp
        
        print(f"Handling time warp: @({at_x},{at_y}) dx={dx} dy={dy} dt={dt} v={value}")  # Debug log
        
        target_time = self.tick - dt
        if target_time < 1:
            target_time = 1
        
        print(f"Time warping from tick {self.tick} to tick {target_time}")  # Debug log
        
        # Restore board to target time
        if target_time <= len(self.history):
            self.board = self.history[target_time - 1].copy()
        else:
            # This shouldn't happen, but handle gracefully
            self.board = self.history[-1].copy()
        
        # Calculate target position relative to @ operator position
        target_x = at_x - dx  # Note: negative dx means left of @
        target_y = at_y - dy  # Note: negative dy means above @
        
        print(f"Writing value {value} to position ({target_x}, {target_y})")  # Debug log
        self.board.set_cell(target_x, target_y, value)
        
        # Truncate history and restart from this point
        self.history = self.history[:target_time]
        self.history.append(self.board.copy())
        self.tick = target_time + 1
        
        print(f"Time warp complete, now at tick {self.tick}")  # Debug log
    
    def _has_reducible_operators(self):
        """Check if any operator on the board can reduce."""
        processor = OperatorProcessor(self.board.copy())
        try:
            time_warps = processor.process_all_operators()
            # If we have pending operations or time warps, something can reduce
            return (len(processor.pending_writes) > 0 or 
                   len(processor.pending_removes) > 0 or 
                   len(time_warps) > 0)
        except:
            return False
    
    def reset(self):
        """Reset simulation to initial state."""
        print(f"Resetting simulator - initial board has {len(self.initial_board.get_all_cells())} cells")  # Debug log
        
        # Clear current board and copy from initial board (with A, B tokens)
        self.board.clear()
        for x, y, value in self.initial_board.get_all_cells():
            self.board.set_cell(x, y, value)
        
        self.tick = 1
        self.history = [self.board.copy()]
        self.running = False
        self.submitted_value = None
        
        print(f"After reset - board has {len(self.board.get_all_cells())} cells")  # Debug log
    
    def start(self):
        """Start the simulation."""
        print("Starting simulation - replacing A, B with input values")  # Debug log
        self._replace_inputs()
        self.running = True
    
    def stop(self):
        """Stop the simulation."""
        self.running = False
    
    def set_inputs(self, input_a, input_b):
        """Set input values and reset simulation."""
        print(f"Setting inputs: A={input_a}, B={input_b}")  # Debug log
        self.input_a = input_a
        self.input_b = input_b
        self.reset()
    
    def get_spacetime_volume(self):
        """Calculate spacetime volume (for scoring)."""
        if not self.history:
            return 0
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        max_t = len(self.history)
        
        for board in self.history:
            if board.grid:
                xs = [x for x, y in board.grid.keys()]
                ys = [y for x, y in board.grid.keys()]
                
                min_x = min(min_x, min(xs))
                max_x = max(max_x, max(xs))
                min_y = min(min_y, min(ys))
                max_y = max(max_y, max(ys))
        
        if min_x == float('inf'):  # No cells ever used
            return 0
        
        vx = max_x - min_x + 1
        vy = max_y - min_y + 1
        vt = max_t
        
        return vx * vy * vt
