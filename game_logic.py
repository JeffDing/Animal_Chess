# 斗兽棋游戏逻辑

class Piece:
    def __init__(self, name, rank, player):
        self.name = name
        self.rank = rank
        self.player = player  # 'red' or 'blue'

    def can_capture(self, other, other_in_trap=False, self_in_river=False, other_in_river=False):
        """检查是否可以吃掉对方棋子

        Args:
            other: 对方的棋子
            other_in_trap: 对方棋子是否在自己的陷阱中
            self_in_river: 自己是否在河中
            other_in_river: 对方是否在河中

        Returns:
            是否可以吃掉对方棋子
        """
        if self.player == other.player:
            return False

        # 如果对方在陷阱中，任何棋子都可以吃掉
        if other_in_trap:
            return True

        # 特殊规则：老鼠在河中不能吃岸上的任何棋子（包括老鼠）
        if self.rank == 1 and self_in_river and not other_in_river:
            return False

        # 特殊规则：老鼠在河中不能吃大象（无论大象在哪里）
        if self.rank == 1 and other.rank == 8 and self_in_river:
            return False

        # 特殊规则：老鼠吃大象（但老鼠必须在陆地上）
        if self.rank == 1 and other.rank == 8 and not self_in_river:
            return True

        # 特殊规则：两只老鼠在河内相遇，可以相互进食
        if self.rank == 1 and other.rank == 1 and self_in_river and other_in_river:
            return True

        # 大吃小（等级高或相等的可以吃）
        if self.rank >= other.rank:
            return True

        return False

class DoushouqiGame:
    def __init__(self):
        self.board = [[None for _ in range(7)] for _ in range(9)]
        self.current_player = 'red'
        self.game_over = False
        self.winner = None
        self.init_board()
        
        # 河流位置
        self.river_positions = [
            (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2),
            (3, 4), (3, 5), (4, 4), (4, 5), (5, 4), (5, 5)
        ]
        
        # 兽穴位置（对换）
        self.den_positions = {
            'red': (8, 3),
            'blue': (0, 3)
        }

        # 陷阱位置（对换）
        self.trap_positions = {
            'red': [(8, 2), (8, 4), (7, 3)],
            'blue': [(0, 2), (0, 4), (1, 3)]
        }

    def init_board(self):
        # 初始化棋子
        pieces = [
            # 红方棋子（原来蓝方的位置）
            ('象', 8, 'red', (8, 6)), ('狮', 7, 'red', (8, 0)),
            ('虎', 6, 'red', (7, 5)), ('豹', 5, 'red', (7, 1)),
            ('狼', 4, 'red', (6, 6)), ('狗', 3, 'red', (6, 0)),
            ('猫', 2, 'red', (7, 6)), ('鼠', 1, 'red', (6, 4)),

            # 蓝方棋子（原来红方的位置）
            ('象', 8, 'blue', (0, 0)), ('狮', 7, 'blue', (0, 6)),
            ('虎', 6, 'blue', (1, 1)), ('豹', 5, 'blue', (1, 5)),
            ('狼', 4, 'blue', (2, 0)), ('狗', 3, 'blue', (2, 6)),
            ('猫', 2, 'blue', (1, 0)), ('鼠', 1, 'blue', (2, 2))
        ]
        
        for name, rank, player, (row, col) in pieces:
            self.board[row][col] = Piece(name, rank, player)

    def is_river(self, row, col):
        return (row, col) in self.river_positions

    def is_trap(self, row, col, player):
        """检查指定位置是否是指定玩家的陷阱

        Args:
            row: 行号
            col: 列号
            player: 玩家（'red' 或 'blue'）

        Returns:
            该位置是否是该玩家的陷阱
        """
        return (row, col) in self.trap_positions[player]

    def is_in_opponent_trap(self, row, col, player):
        """检查指定位置的棋子是否在对方的陷阱中

        Args:
            row: 行号
            col: 列号
            player: 棋子的玩家

        Returns:
            该棋子是否在对方的陷阱中
        """
        opponent = 'blue' if player == 'red' else 'red'
        return (row, col) in self.trap_positions[opponent]

    def is_den(self, row, col, player):
        return (row, col) == self.den_positions[player]

    def is_valid_move(self, from_row, from_col, to_row, to_col, player):
        piece = self.board[from_row][from_col]
        if not piece or piece.player != player:
            return False

        # 检查是否移动到自己的兽穴
        if self.is_den(to_row, to_col, player):
            return False

        # 检查移动距离（只能移动一格）
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)

        # 狮子和老虎可以跳过河流
        if piece.rank in [6, 7]:
            # 检查是否尝试跳过河流
            # 纵向跳跃（从河边跳到对岸）
            if row_diff == 4 and col_diff == 0:
                # 检查是否跨越河流
                river_cells = []
                if from_row < to_row:
                    river_cells = [(from_row + 1, from_col), (from_row + 2, from_col), (from_row + 3, from_col)]
                else:
                    river_cells = [(from_row - 1, from_col), (from_row - 2, from_col), (from_row - 3, from_col)]

                # 检查中间是否都是河流
                if all(self.is_river(r, c) for r, c in river_cells):
                    # 检查河中是否有老鼠阻挡
                    if all(self.board[r][c] is None for r, c in river_cells):
                        # 检查目标位置
                        target = self.board[to_row][to_col]
                        if target:
                            # 如果目标是对手棋子，检查是否可以吃掉
                            if target.player == player:
                                return False

                            # 检查是否可以吃掉目标
                            if not piece.can_capture(target, other_in_trap=False):
                                return False
                        return True
            # 横向跳跃（从河边跳到对岸）
            elif col_diff == 3 and row_diff == 0:
                # 检查是否跨越河流
                river_cells = []
                if from_col < to_col:
                    river_cells = [(from_row, from_col + 1), (from_row, from_col + 2)]
                else:
                    river_cells = [(from_row, from_col - 1), (from_row, from_col - 2)]

                # 检查中间是否都是河流
                if all(self.is_river(r, c) for r, c in river_cells):
                    # 检查河中是否有老鼠阻挡
                    if all(self.board[r][c] is None for r, c in river_cells):
                        # 检查目标位置
                        target = self.board[to_row][to_col]
                        if target:
                            # 如果目标是对手棋子，检查是否可以吃掉
                            if target.player == player:
                                return False

                            # 检查是否可以吃掉目标
                            if not piece.can_capture(target, other_in_trap=False):
                                return False
                        return True

        # 普通移动（每次只能移动一格）
        if row_diff + col_diff != 1:
            return False

        # 检查是否进入河流
        if self.is_river(to_row, to_col) and piece.rank != 1:
            return False

        # 检查目标位置
        target = self.board[to_row][to_col]
        if target:
            if target.player == player:
                return False

            # 检查目标棋子是否在当前玩家的陷阱中（即目标棋子在对方的陷阱中）
            target_in_my_trap = self.is_in_opponent_trap(to_row, to_col, target.player)

            # 检查目标棋子是否在它自己的陷阱中（如果在自己陷阱中，不能被吃掉）
            target_in_its_own_trap = self.is_trap(to_row, to_col, target.player)

            # 如果目标棋子在它自己的陷阱中，不能被吃掉
            if target_in_its_own_trap:
                return False

            # 检查是否可以吃掉目标
            self_in_river = self.is_river(from_row, from_col)
            other_in_river = self.is_river(to_row, to_col)

            if not piece.can_capture(target, target_in_my_trap, self_in_river, other_in_river):
                return False

            # 老鼠不能从水里吃岸上的棋子
            if piece.rank == 1 and self_in_river and not other_in_river:
                return False

            # 岸上的棋子不能吃水里的老鼠
            if piece.rank != 1 and not self_in_river and other_in_river:
                return False

        return True

    def make_move(self, from_row, from_col, to_row, to_col):
        if self.game_over:
            return False
        
        if not self.is_valid_move(from_row, from_col, to_row, to_col, self.current_player):
            return False
        
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # 检查是否吃掉对方兽穴
        opponent = 'blue' if self.current_player == 'red' else 'red'
        if self.is_den(to_row, to_col, opponent):
            self.game_over = True
            self.winner = self.current_player
            return True
        
        # 检查是否吃掉对方所有棋子
        opponent_pieces = 0
        for row in range(9):
            for col in range(7):
                p = self.board[row][col]
                if p and p.player == opponent:
                    opponent_pieces += 1
        
        if opponent_pieces == 0:
            self.game_over = True
            self.winner = self.current_player
            return True
        
        # 切换玩家
        self.current_player = opponent
        return True

    def get_valid_moves(self, player):
        moves = []
        for from_row in range(9):
            for from_col in range(7):
                piece = self.board[from_row][from_col]
                if piece and piece.player == player:
                    for to_row in range(9):
                        for to_col in range(7):
                            if self.is_valid_move(from_row, from_col, to_row, to_col, player):
                                moves.append((from_row, from_col, to_row, to_col))
        return moves

    def get_board_state(self):
        state = []
        for row in range(9):
            row_state = []
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    row_state.append({
                        'name': piece.name,
                        'rank': piece.rank,
                        'player': piece.player
                    })
                else:
                    row_state.append(None)
            state.append(row_state)
        return state

    def clone(self):
        new_game = DoushouqiGame()
        new_game.board = [[None for _ in range(7)] for _ in range(9)]
        for row in range(9):
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    new_game.board[row][col] = Piece(piece.name, piece.rank, piece.player)
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        return new_game
