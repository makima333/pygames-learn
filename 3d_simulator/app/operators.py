"""
Operator processing for the 3D language simulator.
"""

class OperatorProcessor:
    def __init__(self, board):
        self.board = board
        self.pending_writes = []  # [(x, y, value), ...]
        self.pending_removes = []  # [(x, y), ...]
        self.time_warps = []  # [(dx, dy, dt, value), ...]
        
    def process_all_operators(self):
        """Process all operators on the board for one tick."""
        self.pending_writes.clear()
        self.pending_removes.clear()
        self.time_warps.clear()
        
        # Collect all operations first - only process actual operators
        for x, y, value in self.board.get_all_cells():
            if self._is_operator(value):
                self._process_operator_at(x, y, value)
        
        # Apply all removes first
        for x, y in self.pending_removes:
            self.board.set_cell(x, y, None)
        
        # Check for write conflicts
        write_positions = {}
        for x, y, value in self.pending_writes:
            if (x, y) in write_positions:
                if write_positions[(x, y)] != value:
                    raise RuntimeError(f"Write conflict at ({x}, {y}): {write_positions[(x, y)]} vs {value}")
            write_positions[(x, y)] = value
        
        # Apply all writes
        for x, y, value in self.pending_writes:
            self.board.set_cell(x, y, value)
        
        # Check for time warp conflicts
        if len(self.time_warps) > 1:
            dts = [warp[4] for warp in self.time_warps]  # dt is now at index 4
            if len(set(dts)) > 1:
                raise RuntimeError("Multiple time warps to different times in same tick")
        
        return self.time_warps
    
    def _is_operator(self, value):
        """Check if value is an operator."""
        if isinstance(value, int):
            return False  # Numbers are not operators
        
        operators = {'<', '>', '^', 'v', '+', '-', '*', '/', '%', '@', '=', '#', 'S', 'A', 'B'}
        return value in operators
    
    def _process_operator_at(self, x, y, operator):
        """Process a single operator at given position."""
        print(f"Processing operator '{operator}' at ({x}, {y})")  # Debug log
        
        if operator == '<':
            self._process_move_left(x, y)
        elif operator == '>':
            self._process_move_right(x, y)
        elif operator == '^':
            self._process_move_up(x, y)
        elif operator == 'v':
            self._process_move_down(x, y)
        elif operator == '+':
            self._process_binary_op(x, y, lambda a, b: a + b)
        elif operator == '-':
            self._process_binary_op(x, y, lambda a, b: a - b)
        elif operator == '*':
            self._process_binary_op(x, y, lambda a, b: a * b)
        elif operator == '/':
            self._process_binary_op(x, y, lambda a, b: int(a / b) if b != 0 else 0)
        elif operator == '%':
            self._process_binary_op(x, y, lambda a, b: a % b if b != 0 else 0)
        elif operator == '=':
            self._process_equality(x, y)
        elif operator == '#':
            self._process_not_equal(x, y)
        elif operator == '@':
            self._process_time_warp(x, y)
    
    def _process_move_left(self, x, y):
        """Process < operator: . < x -> x < ."""
        right_val = self.board.get_cell(x + 1, y)
        if right_val is not None:
            self.pending_removes.append((x + 1, y))
            self.pending_writes.append((x - 1, y, right_val))
    
    def _process_move_right(self, x, y):
        """Process > operator: x > . -> . > x"""
        left_val = self.board.get_cell(x - 1, y)
        print(f"Move right at ({x}, {y}): left_val = {left_val}")  # Debug log
        if left_val is not None:
            print(f"Moving {left_val} from ({x-1}, {y}) to ({x+1}, {y})")  # Debug log
            self.pending_removes.append((x - 1, y))
            self.pending_writes.append((x + 1, y, left_val))
    
    def _process_move_up(self, x, y):
        """Process ^ operator: move value from below to above"""
        below_val = self.board.get_cell(x, y + 1)
        if below_val is not None:
            self.pending_removes.append((x, y + 1))
            self.pending_writes.append((x, y - 1, below_val))
    
    def _process_move_down(self, x, y):
        """Process v operator: move value from above to below"""
        above_val = self.board.get_cell(x, y - 1)
        if above_val is not None:
            self.pending_removes.append((x, y - 1))
            self.pending_writes.append((x, y + 1, above_val))
    
    def _process_binary_op(self, x, y, operation):
        """Process binary operators like +, -, *, /, %"""
        left_val = self.board.get_cell(x - 1, y)
        above_val = self.board.get_cell(x, y - 1)
        
        if (left_val is not None and isinstance(left_val, int) and 
            above_val is not None and isinstance(above_val, int)):
            
            try:
                # For binary operators: left_val is x, above_val is y
                # So the operation is x op y (e.g., x / y)
                result = operation(left_val, above_val)
                self.pending_removes.append((x - 1, y))
                self.pending_removes.append((x, y - 1))
                self.pending_writes.append((x + 1, y, result))
                self.pending_writes.append((x, y + 1, result))
            except (ZeroDivisionError, ValueError):
                pass  # Operation failed, no change
    
    def _process_equality(self, x, y):
        """Process = operator: only reduces if operands are equal"""
        left_val = self.board.get_cell(x - 1, y)
        above_val = self.board.get_cell(x, y - 1)
        
        if (left_val is not None and above_val is not None and left_val == above_val):
            self.pending_removes.append((x - 1, y))
            self.pending_removes.append((x, y - 1))
            self.pending_writes.append((x + 1, y, left_val))
            self.pending_writes.append((x, y + 1, left_val))
    
    def _process_not_equal(self, x, y):
        """Process # operator: only reduces if operands are not equal"""
        left_val = self.board.get_cell(x - 1, y)
        above_val = self.board.get_cell(x, y - 1)
        
        if (left_val is not None and above_val is not None and left_val != above_val):
            self.pending_removes.append((x - 1, y))
            self.pending_removes.append((x, y - 1))
            self.pending_writes.append((x + 1, y, left_val))
            self.pending_writes.append((x, y + 1, left_val))
    
    def _process_time_warp(self, x, y):
        """Process @ operator: time warp"""
        print(f"Processing time warp at ({x}, {y})")  # Debug log
        
        # Get the four values around @
        above_val = self.board.get_cell(x, y - 1)  # v
        left_val = self.board.get_cell(x - 1, y)   # dx
        right_val = self.board.get_cell(x + 1, y)  # dy
        below_val = self.board.get_cell(x, y + 1)  # dt
        
        print(f"Time warp values: v={above_val}, dx={left_val}, dy={right_val}, dt={below_val}")  # Debug log
        
        if (above_val is not None and 
            isinstance(left_val, int) and isinstance(right_val, int) and 
            isinstance(below_val, int) and below_val >= 1):
            
            # Store the @ operator position along with the warp parameters
            self.time_warps.append((x, y, left_val, right_val, below_val, above_val))
            # Remove the consumed values
            self.pending_removes.append((x, y - 1))
            self.pending_removes.append((x - 1, y))
            self.pending_removes.append((x + 1, y))
            self.pending_removes.append((x, y + 1))
            print(f"Time warp scheduled: @({x},{y}) dx={left_val} dy={right_val} dt={below_val} v={above_val}")  # Debug log
        else:
            print(f"Time warp conditions not met")  # Debug log
