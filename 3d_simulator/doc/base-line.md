## ミニマム基本設計

### 1. 核心機能のみに絞った構成

#### 1.1 必須機能
• **グリッドエディタ**: 基本的な2Dグリッド編集
• **シンプル実行**: ステップ実行のみ
• **基本視覚化**: 静的なグリッド表示
• **演算子処理**: 全演算子の基本動作

#### 1.2 除外する機能（後回し）
• アニメーション
• ファイル保存/読み込み
• デバッグ機能
• チュートリアル
• 統計・スコア表示

### 2. アーキテクチャ設計

main.py
├── GameEngine (ゲーム全体制御)
├── Board (2Dグリッド管理)
├── Simulator (3D言語実行エンジン)
├── UI (pygame描画・入力処理)
└── Operators (演算子処理)


### 3. クラス設計

#### 3.1 Board クラス
python
class Board:
    def __init__(self, width=20, height=15):
        self.grid = {}  # {(x,y): value}
        self.width = width
        self.height = height

    def set_cell(self, x, y, value)
    def get_cell(self, x, y)
    def is_empty(self, x, y)
    def get_all_cells()


#### 3.2 Simulator クラス
python
class Simulator:
    def __init__(self, board):
        self.board = board
        self.tick = 1
        self.history = []  # 時間旅行用
        self.running = False

    def step()  # 1tick実行
    def reset()
    def process_operators()
    def handle_time_warp()


#### 3.3 UI クラス
python
class UI:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen = pygame.display.set_mode((width, height))
        self.cell_size = 30
        self.selected_cell = None

    def draw_grid()
    def draw_cell_values()
    def handle_mouse_click()
    def handle_keyboard_input()


#### 3.4 GameEngine クラス
python
class GameEngine:
    def __init__(self):
        self.board = Board()
        self.simulator = Simulator(self.board)
        self.ui = UI()
        self.input_a = 0
        self.input_b = 0

    def run()  # メインループ
    def handle_events()
    def update()
    def render()


### 4. ミニマムUI設計

#### 4.1 画面レイアウト
┌─────────────────────────────────────┐
│ [Step] [Reset] A:[ 0] B:[ 0] T:001  │ ← 制御パネル
├─────────────────────────────────────┤
│                                     │
│        ┌─┬─┬─┬─┬─┐                │
│        │.│1│>│.│.│                │
│        ├─┼─┼─┼─┼─┤                │
│        │A│+│B│=│S│  ← グリッド     │
│        ├─┼─┼─┼─┼─┤                │
│        │.│.│.│.│.│                │
│        └─┴─┴─┴─┴─┘                │
│                                     │
├─────────────────────────────────────┤
│ Status: Ready                       │ ← ステータス
└─────────────────────────────────────┘


#### 4.2 操作方法
• **マウスクリック**: セル選択・編集
• **キーボード**: 数値・演算子入力
• **Spaceキー**: ステップ実行
• **Rキー**: リセット

### 5. データ構造

#### 5.1 セル値の表現
python
# 空セル
None または '.'

# 数値
int (-99 ≤ n ≤ 99)

# 演算子
str ('<', '>', '^', 'v', '+', '-', '*', '/', '%', '@', '=', '#', 'S', 'A', 'B')


#### 5.2 ボード状態
python
{
    (0, 0): '.',
    (1, 0): 5,
    (2, 0): '>',
    (3, 0): '.',
    # ...
}


### 6. 実装優先順位

#### Phase 1: 基本フレームワーク
1. pygame初期化とメインループ
2. グリッド描画
3. マウス/キーボード入力処理

#### Phase 2: コア機能
1. Board クラス実装
2. 基本演算子（移動系: <, >, ^, v）
3. ステップ実行機能

#### Phase 3: 演算子拡張
1. 算術演算子（+, -, , /, %）
2. 比較演算子（=, #）
3. 入力/出力（A, B, S）

#### Phase 4: 時間旅行
1. 履歴管理
2. ワープ演算子（@）実装

### 7. ファイル構成

3d_simulator/
├── main.py           # エントリーポイント
├── board.py          # Board クラス
├── simulator.py      # Simulator クラス
├── ui.py            # UI クラス
├── operators.py     # 演算子処理
└── game_engine.py   # GameEngine クラス


### 8. 最小動作例

python
# 簡単なテストケース
# A + B = S の実装
grid = {
    (0, 0): 'A',  # 入力A
    (1, 0): '+',  # 加算
    (2, 0): 'B',  # 入力B
    (3, 0): '=',  # 等号（結果転送用）
    (4, 0): 'S'   # 出力
}
