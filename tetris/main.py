import pygame
import random
import sys
from typing import List, Tuple, Optional

# 初期化
pygame.init()

# 定数
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50

# 画面サイズ
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + GRID_X_OFFSET * 2 + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + GRID_Y_OFFSET * 2

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# テトリミノの形状定義
TETROMINOS = {
    'I': [
        ['.....',
         '..#..',
         '..#..',
         '..#..',
         '..#..'],
        ['.....',
         '.....',
         '####.',
         '.....',
         '.....']
    ],
    'O': [
        ['.....',
         '.....',
         '.##..',
         '.##..',
         '.....']
    ],
    'T': [
        ['.....',
         '.....',
         '.#...',
         '###..',
         '.....'],
        ['.....',
         '.....',
         '.#...',
         '.##..',
         '.#...'],
        ['.....',
         '.....',
         '.....',
         '###..',
         '.#...'],
        ['.....',
         '.....',
         '.#...',
         '##...',
         '.#...']
    ],
    'S': [
        ['.....',
         '.....',
         '.##..',
         '##...',
         '.....'],
        ['.....',
         '.#...',
         '.##..',
         '..#..',
         '.....']
    ],
    'Z': [
        ['.....',
         '.....',
         '##...',
         '.##..',
         '.....'],
        ['.....',
         '..#..',
         '.##..',
         '.#...',
         '.....']
    ],
    'J': [
        ['.....',
         '.#...',
         '.#...',
         '##...',
         '.....'],
        ['.....',
         '.....',
         '#....',
         '###..',
         '.....'],
        ['.....',
         '.##..',
         '.#...',
         '.#...',
         '.....'],
        ['.....',
         '.....',
         '###..',
         '..#..',
         '.....']
    ],
    'L': [
        ['.....',
         '..#..',
         '..#..',
         '.##..',
         '.....'],
        ['.....',
         '.....',
         '###..',
         '#....',
         '.....'],
        ['.....',
         '##...',
         '.#...',
         '.#...',
         '.....'],
        ['.....',
         '.....',
         '..#..',
         '###..',
         '.....']
    ]
}

# テトリミノの色
TETROMINO_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class Tetromino:
    def __init__(self, shape: str):
        self.shape = shape
        self.color = TETROMINO_COLORS[shape]
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0
        
    def get_rotated_shape(self) -> List[str]:
        """現在の回転状態の形状を取得"""
        return TETROMINOS[self.shape][self.rotation % len(TETROMINOS[self.shape])]
    
    def get_cells(self) -> List[Tuple[int, int]]:
        """テトリミノが占有するセルの座標リストを取得"""
        cells = []
        shape = self.get_rotated_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + j, self.y + i))
        return cells

class TetrisGame:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # ミリ秒
        self.game_over = False
        
        # 最初のピースを生成
        self.spawn_new_piece()
        self.next_piece = self.create_random_piece()
    
    def create_random_piece(self) -> Tetromino:
        """ランダムなテトリミノを生成"""
        shape = random.choice(list(TETROMINOS.keys()))
        return Tetromino(shape)
    
    def spawn_new_piece(self):
        """新しいピースをスポーン"""
        if self.next_piece:
            self.current_piece = self.next_piece
            self.next_piece = self.create_random_piece()
        else:
            self.current_piece = self.create_random_piece()
        
        # ゲームオーバー判定
        if self.is_collision(self.current_piece):
            self.game_over = True
    
    def is_collision(self, piece: Tetromino, dx: int = 0, dy: int = 0, rotation: int = None) -> bool:
        """衝突判定"""
        if rotation is not None:
            # 回転後の形状で判定
            original_rotation = piece.rotation
            piece.rotation = rotation
            cells = piece.get_cells()
            piece.rotation = original_rotation
        else:
            cells = piece.get_cells()
        
        for x, y in cells:
            new_x, new_y = x + dx, y + dy
            
            # 境界チェック
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return True
            
            # グリッドとの衝突チェック
            if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                return True
        
        return False
    
    def move_piece(self, dx: int, dy: int) -> bool:
        """ピースを移動"""
        if not self.current_piece or self.game_over:
            return False
        
        if not self.is_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self) -> bool:
        """ピースを回転"""
        if not self.current_piece or self.game_over:
            return False
        
        new_rotation = (self.current_piece.rotation + 1) % len(TETROMINOS[self.current_piece.shape])
        
        if not self.is_collision(self.current_piece, rotation=new_rotation):
            self.current_piece.rotation = new_rotation
            return True
        return False
    
    def lock_piece(self):
        """ピースをグリッドに固定"""
        if not self.current_piece:
            return
        
        for x, y in self.current_piece.get_cells():
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.grid[y][x] = self.current_piece.color
        
        # ライン消去チェック
        self.clear_lines()
        
        # 新しいピースをスポーン
        self.spawn_new_piece()
    
    def clear_lines(self):
        """完成したラインを消去"""
        lines_to_clear = []
        
        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        # ラインを消去
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        # スコア計算
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            line_score = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += line_score.get(len(lines_to_clear), 0) * self.level
            
            # レベルアップ
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def update(self, dt: int):
        """ゲーム状態を更新"""
        if self.game_over:
            return
        
        self.fall_time += dt
        
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.fall_time = 0
    
    def hard_drop(self):
        """ハードドロップ"""
        if not self.current_piece or self.game_over:
            return
        
        while self.move_piece(0, 1):
            self.score += 2
        
        self.lock_piece()

def draw_grid(screen: pygame.Surface, game: TetrisGame):
    """グリッドを描画"""
    # グリッドの背景
    grid_rect = pygame.Rect(GRID_X_OFFSET, GRID_Y_OFFSET, 
                           GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
    pygame.draw.rect(screen, WHITE, grid_rect)
    pygame.draw.rect(screen, BLACK, grid_rect, 2)
    
    # 固定されたブロック
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if game.grid[y][x] != BLACK:
                rect = pygame.Rect(GRID_X_OFFSET + x * CELL_SIZE,
                                 GRID_Y_OFFSET + y * CELL_SIZE,
                                 CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, game.grid[y][x], rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
    
    # 現在のピース
    if game.current_piece:
        for x, y in game.current_piece.get_cells():
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                rect = pygame.Rect(GRID_X_OFFSET + x * CELL_SIZE,
                                 GRID_Y_OFFSET + y * CELL_SIZE,
                                 CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, game.current_piece.color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

def draw_next_piece(screen: pygame.Surface, game: TetrisGame):
    """次のピースを描画"""
    if not game.next_piece:
        return
    
    # 次のピース表示エリア
    next_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
    next_y = GRID_Y_OFFSET + 50
    
    font = pygame.font.Font(None, 24)
    text = font.render("NEXT", True, WHITE)
    screen.blit(text, (next_x, next_y - 30))
    
    # 次のピースの形状を描画
    shape = game.next_piece.get_rotated_shape()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == '#':
                rect = pygame.Rect(next_x + j * 20, next_y + i * 20, 20, 20)
                pygame.draw.rect(screen, game.next_piece.color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

def draw_info(screen: pygame.Surface, game: TetrisGame):
    """ゲーム情報を描画"""
    info_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
    info_y = GRID_Y_OFFSET + 200
    
    font = pygame.font.Font(None, 24)
    
    # スコア
    score_text = font.render(f"SCORE: {game.score}", True, WHITE)
    screen.blit(score_text, (info_x, info_y))
    
    # レベル
    level_text = font.render(f"LEVEL: {game.level}", True, WHITE)
    screen.blit(level_text, (info_x, info_y + 30))
    
    # ライン数
    lines_text = font.render(f"LINES: {game.lines_cleared}", True, WHITE)
    screen.blit(lines_text, (info_x, info_y + 60))

def draw_game_over(screen: pygame.Surface, game: TetrisGame):
    """ゲームオーバー画面を描画"""
    if not game.game_over:
        return
    
    # 半透明のオーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # ゲームオーバーテキスト
    font = pygame.font.Font(None, 48)
    game_over_text = font.render("GAME OVER", True, WHITE)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text, text_rect)
    
    # 最終スコア
    score_text = font.render(f"Final Score: {game.score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(score_text, score_rect)
    
    # リスタート指示
    restart_font = pygame.font.Font(None, 24)
    restart_text = restart_font.render("Press R to restart or ESC to quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    game = TetrisGame()
    
    # キーリピート設定
    pygame.key.set_repeat(250, 50)
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        # ゲームリスタート
                        game = TetrisGame()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                else:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        if game.move_piece(0, 1):
                            game.score += 1
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
        
        # ゲーム更新
        game.update(dt)
        
        # 描画
        screen.fill(BLACK)
        draw_grid(screen, game)
        draw_next_piece(screen, game)
        draw_info(screen, game)
        draw_game_over(screen, game)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
