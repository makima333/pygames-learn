"""
Board class for managing the 2D grid of the 3D language simulator.
"""

class Board:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.grid = {}  # {(x, y): value}
        
    def set_cell(self, x, y, value):
        """Set a cell value. None or '.' represents empty cell."""
        if value is None or value == '.':
            if (x, y) in self.grid:
                del self.grid[(x, y)]
        else:
            self.grid[(x, y)] = value
    
    def get_cell(self, x, y):
        """Get cell value. Returns None for empty cells."""
        return self.grid.get((x, y), None)
    
    def is_empty(self, x, y):
        """Check if cell is empty."""
        return (x, y) not in self.grid
    
    def get_all_cells(self):
        """Get all non-empty cells as list of (x, y, value) tuples."""
        return [(x, y, value) for (x, y), value in self.grid.items()]
    
    def clear(self):
        """Clear all cells."""
        self.grid.clear()
    
    def copy(self):
        """Create a deep copy of the board."""
        new_board = Board(self.width, self.height)
        new_board.grid = self.grid.copy()
        return new_board
    
    def get_bounds(self):
        """Get the actual bounds of non-empty cells."""
        if not self.grid:
            return 0, 0, 0, 0
        
        xs = [x for x, y in self.grid.keys()]
        ys = [y for x, y in self.grid.keys()]
        
        return min(xs), max(xs), min(ys), max(ys)
    
    def is_valid_token(self, token):
        """Check if token is valid for 3D language."""
        if token is None or token == '.':
            return True
        
        # Integer between -99 and 99
        if isinstance(token, int):
            return -99 <= token <= 99
        
        # Try to parse as integer
        if isinstance(token, str):
            try:
                val = int(token)
                return -99 <= val <= 99
            except ValueError:
                pass
        
        # Operators
        valid_operators = {'<', '>', '^', 'v', '+', '-', '*', '/', '%', '@', '=', '#', 'S', 'A', 'B'}
        return token in valid_operators
