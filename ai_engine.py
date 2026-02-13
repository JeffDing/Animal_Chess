"""
斗兽棋AI引擎
实现Minimax算法和Alpha-Beta剪枝，提供不同难度的AI
"""

import random
import math
import time
from typing import Optional, Tuple, List


class DoushouqiAI:
    """斗兽棋AI引擎"""

    def __init__(self, difficulty='medium'):
        """
        初始化AI

        Args:
            difficulty: AI难度 ('beginner', 'easy', 'amateur', 'professional', 'master')
        """
        self.difficulty = difficulty
        self.max_depth = self._get_max_depth()
        self.thinking_time = self._get_thinking_time()
        self.position_table = self._init_position_table()
        self.transposition_table = {}  # 换位表，缓存搜索结果
        self.search_count = 0  # 搜索节点计数

    def _get_max_depth(self):
        """根据难度获取搜索深度"""
        depth_map = {
            'beginner': 1,        # 入门：搜索深度1，基本不思考
            'easy': 2,            # 简单：搜索深度2，少量前瞻
            'amateur': 4,         # 业余：搜索深度4
            'professional': 6,    # 专业：搜索深度6
            'master': 15          # 大师：搜索深度15，配合迭代加深，人类难以战胜
        }
        return depth_map.get(self.difficulty, 2)

    def _get_thinking_time(self):
        """根据难度获取思考时间（秒）"""
        time_map = {
            'beginner': 0.1,      # 入门：几乎不思考
            'easy': 0.3,          # 简单：快速决策
            'amateur': 0.8,       # 业余：正常思考
            'professional': 2.0,  # 专业：较长时间思考
            'master': 10.0        # 大师：极限深度思考，人类难以战胜
        }
        return time_map.get(self.difficulty, 0.8)

    def _init_position_table(self):
        """初始化位置价值表，评估棋盘上不同位置的价值"""
        # 基础位置价值，越靠近对方兽穴价值越高
        position_value = []
        for row in range(9):
            row_values = []
            for col in range(7):
                # 蓝方（上方）向下的价值
                blue_value = row * 10
                # 红方（下方）向上的价值
                red_value = (8 - row) * 10

                # 河流位置的价值调整
                if (row, col) in [(3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2),
                                  (3, 4), (3, 5), (4, 4), (4, 5), (5, 4), (5, 5)]:
                    # 河流对老鼠有价值，对其他棋子价值低
                    blue_value = 5
                    red_value = 5

                row_values.append({
                    'blue': blue_value,
                    'red': red_value
                })
            position_value.append(row_values)
        return position_value

    def get_best_move(self, game, player) -> Optional[Tuple[int, int, int, int]]:
        """
        获取最佳移动

        Args:
            game: 游戏实例
            player: 当前玩家 ('red' 或 'blue')

        Returns:
            最佳移动 (from_row, from_col, to_row, to_col)
        """
        # 获取所有有效移动
        valid_moves = game.get_valid_moves(player)

        if not valid_moves:
            return None

        # 清空换位表和计数器
        self.transposition_table.clear()
        self.search_count = 0

        # 根据难度选择策略
        if self.difficulty == 'beginner':
            # 入门：85%概率随机移动，15%概率使用算法
            if random.random() < 0.85:
                return self._get_random_move(valid_moves)
            else:
                return self._minimax_with_alpha_beta(game, player, self.max_depth)
        elif self.difficulty == 'easy':
            # 简单：40%概率随机移动，60%概率使用算法
            if random.random() < 0.4:
                return self._get_random_move(valid_moves)
            else:
                return self._minimax_with_alpha_beta(game, player, self.max_depth)
        elif self.difficulty == 'amateur':
            # 业余：15%概率随机移动，85%概率使用算法
            if random.random() < 0.15:
                return self._get_random_move(valid_moves)
            else:
                return self._minimax_with_alpha_beta(game, player, self.max_depth)
        elif self.difficulty == 'professional':
            # 专业：5%概率随机移动，95%概率使用算法
            if random.random() < 0.05:
                return self._get_random_move(valid_moves)
            else:
                return self._minimax_with_alpha_beta(game, player, self.max_depth)
        else:  # master
            # 大师：100%使用算法，使用迭代加深搜索
            return self._iterative_deepening_search(game, player)

    def _get_random_move(self, valid_moves):
        """简单AI：随机选择移动"""
        return random.choice(valid_moves)

    def _iterative_deepening_search(self, game, player) -> Optional[Tuple[int, int, int, int]]:
        """
        迭代加深搜索（大师级专用）
        在时间限制内不断加深搜索深度，找到最佳移动

        Args:
            game: 游戏实例
            player: 当前玩家

        Returns:
            最佳移动
        """
        start_time = time.time()
        best_move = None
        best_score = -float('inf')

        # 获取有效移动并排序
        valid_moves = game.get_valid_moves(player)
        if not valid_moves:
            return None

        sorted_moves = self._sort_moves(game, valid_moves, player)

        # 从深度1开始，逐步加深
        for depth in range(1, self.max_depth + 1):
            # 检查时间
            elapsed = time.time() - start_time
            if elapsed > self.thinking_time * 0.9:  # 留10%时间用于返回
                break

            # 在当前深度搜索
            current_best = None
            current_best_score = -float('inf')
            alpha = -float('inf')
            beta = float('inf')

            for move in sorted_moves:
                temp_game = game.clone()
                temp_game.make_move(move[0], move[1], move[2], move[3])

                score = self._minimax(temp_game, depth - 1, alpha, beta, False, player)

                if score > current_best_score:
                    current_best_score = score
                    current_best = move

                alpha = max(alpha, score)

                if beta <= alpha:
                    break

            # 如果找到必胜移动，直接返回
            if current_best_score >= 10000:
                return current_best

            # 更新最佳移动
            if current_best_score > best_score:
                best_score = current_best_score
                best_move = current_best

        return best_move

    def _minimax_with_alpha_beta(self, game, player, depth) -> Optional[Tuple[int, int, int, int]]:
        """
        使用Minimax算法和Alpha-Beta剪枝找到最佳移动

        Args:
            game: 游戏实例
            player: 当前玩家
            depth: 搜索深度

        Returns:
            最佳移动
        """
        valid_moves = game.get_valid_moves(player)

        if not valid_moves:
            return None

        best_move = None
        best_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        # 排序移动以优化剪枝（优先考虑吃子和有价值的移动）
        sorted_moves = self._sort_moves(game, valid_moves, player)

        for move in sorted_moves:
            # 模拟移动
            temp_game = game.clone()
            temp_game.make_move(move[0], move[1], move[2], move[3])

            # 递归搜索
            score = self._minimax(temp_game, depth - 1, alpha, beta, False, player)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

            # 如果beta <= alpha，剪枝
            if beta <= alpha:
                break

        return best_move

    def _minimax(self, game, depth, alpha, beta, is_maximizing, player):
        """
        Minimax算法的递归实现

        Args:
            game: 游戏实例
            depth: 当前深度
            alpha: Alpha值
            beta: Beta值
            is_maximizing: 是否是最大化层
            player: 原始玩家

        Returns:
            评估分数
        """
        # 检查游戏是否结束
        if game.game_over:
            return self._evaluate_terminal_state(game, player)

        # 达到最大深度，评估当前局面
        if depth == 0:
            return self._evaluate_board(game, player)

        # 生成棋盘状态的哈希键（用于换位表）
        board_key = self._get_board_key(game, player, depth)

        # 检查换位表
        if board_key in self.transposition_table:
            stored_entry = self.transposition_table[board_key]
            if stored_entry['depth'] >= depth:
                # 如果存储的深度>=当前深度，可以直接使用
                if stored_entry['flag'] == 'exact':
                    return stored_entry['score']
                elif stored_entry['flag'] == 'lower' and stored_entry['score'] >= beta:
                    return stored_entry['score']
                elif stored_entry['flag'] == 'upper' and stored_entry['score'] <= alpha:
                    return stored_entry['score']

        self.search_count += 1
        current_player = game.current_player

        if is_maximizing:
            max_eval = -float('inf')
            valid_moves = game.get_valid_moves(current_player)

            if not valid_moves:
                # 无路可走，当前玩家输
                return -10000 if current_player == player else 10000

            sorted_moves = self._sort_moves(game, valid_moves, current_player)

            for move in sorted_moves:
                temp_game = game.clone()
                temp_game.make_move(move[0], move[1], move[2], move[3])

                eval_score = self._minimax(temp_game, depth - 1, alpha, beta, False, player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break

            # 存储到换位表
            self._store_transposition(board_key, max_eval, depth, alpha, beta, 'lower')

            return max_eval
        else:
            min_eval = float('inf')
            valid_moves = game.get_valid_moves(current_player)

            if not valid_moves:
                # 无路可走，当前玩家输
                return 10000 if current_player == player else -10000

            sorted_moves = self._sort_moves(game, valid_moves, current_player)

            for move in sorted_moves:
                temp_game = game.clone()
                temp_game.make_move(move[0], move[1], move[2], move[3])

                eval_score = self._minimax(temp_game, depth - 1, alpha, beta, True, player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break

            # 存储到换位表
            self._store_transposition(board_key, min_eval, depth, alpha, beta, 'upper')

            return min_eval

    def _get_board_key(self, game, player, depth):
        """生成棋盘状态的哈希键"""
        key_parts = []
        for row in range(9):
            for col in range(7):
                piece = game.board[row][col]
                if piece:
                    key_parts.append(f"{row}{col}{piece.player}{piece.rank}")
                else:
                    key_parts.append(f"{row}{col}N")
        key_parts.append(player)
        key_parts.append(str(depth))
        return ''.join(key_parts)

    def _store_transposition(self, key, score, depth, alpha, beta, flag):
        """存储到换位表"""
        if len(self.transposition_table) > 100000:  # 限制表大小
            self.transposition_table.clear()

        if score <= alpha:
            stored_flag = 'upper'
        elif score >= beta:
            stored_flag = 'lower'
        else:
            stored_flag = 'exact'

        self.transposition_table[key] = {
            'score': score,
            'depth': depth,
            'flag': stored_flag
        }

    def _sort_moves(self, game, moves, player):
        """
        对移动进行排序，优先考虑有价值的移动

        Args:
            game: 游戏实例
            moves: 移动列表
            player: 玩家

        Returns:
            排序后的移动列表
        """
        move_scores = []

        for move in moves:
            from_row, from_col, to_row, to_col = move
            score = 0

            # 优先考虑吃子
            target_piece = game.board[to_row][to_col]
            if target_piece and target_piece.player != player:
                score += target_piece.rank * 100

            # 优先考虑进入对方兽穴
            opponent = 'blue' if player == 'red' else 'red'
            if (to_row, to_col) == game.den_positions[opponent]:
                score += 1000

            # 优先考虑靠近对方兽穴
            den_pos = game.den_positions[opponent]
            distance_to_den = abs(to_row - den_pos[0]) + abs(to_col - den_pos[1])
            score += (12 - distance_to_den) * 5

            move_scores.append((score, move))

        # 按分数降序排序
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in move_scores]

    def _evaluate_terminal_state(self, game, player):
        """评估终局状态"""
        if game.winner == player:
            return 10000  # 获胜
        else:
            return -10000  # 失败

    def _evaluate_board(self, game, player):
        """
        评估当前棋盘状态

        Args:
            game: 游戏实例
            player: 玩家

        Returns:
            评估分数
        """
        score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 棋子价值表（根据难度调整）
        if self.difficulty == 'master':
            piece_values = {
                1: 300,   # 鼠（特殊价值，可以吃象，且能过河）
                2: 350,   # 猫
                3: 420,   # 狗
                4: 500,   # 狼
                5: 580,   # 豹
                6: 1000,  # 虎
                7: 1200,  # 狮
                8: 1500   # 象
            }
        elif self.difficulty == 'professional':
            piece_values = {
                1: 200,   # 鼠（特殊价值，可以吃象）
                2: 280,   # 猫
                3: 380,   # 狗
                4: 480,   # 狼
                5: 550,   # 豹
                6: 900,   # 虎
                7: 1000,  # 狮
                8: 1200   # 象
            }
        elif self.difficulty == 'amateur':
            piece_values = {
                1: 150,   # 鼠
                2: 220,   # 猫
                3: 330,   # 狗
                4: 440,   # 狼
                5: 500,   # 豹
                6: 800,   # 虎
                7: 900,   # 狮
                8: 1000   # 象
            }
        elif self.difficulty == 'easy':
            piece_values = {
                1: 100,   # 鼠
                2: 180,   # 猫
                3: 280,   # 狗
                4: 380,   # 狼
                5: 450,   # 豹
                6: 700,   # 虎
                7: 800,   # 狮
                8: 900    # 象
            }
        else:  # beginner
            piece_values = {
                1: 80,    # 鼠
                2: 150,   # 猫
                3: 250,   # 狗
                4: 350,   # 狼
                5: 400,   # 豹
                6: 600,   # 虎
                7: 700,   # 狮
                8: 800    # 象
            }

        # 统计双方棋子
        my_pieces = []
        opponent_pieces = []

        for row in range(9):
            for col in range(7):
                piece = game.board[row][col]
                if piece:
                    if piece.player == player:
                        my_pieces.append((piece, row, col))
                    else:
                        opponent_pieces.append((piece, row, col))

        # 1. 开局库（大师级和专业级）
        if self.difficulty in ['master', 'professional']:
            opening_score = self._evaluate_opening(game, player, my_pieces, opponent_pieces)
            score += opening_score

        # 2. 材质价值
        for piece, row, col in my_pieces:
            score += piece_values.get(piece.rank, 0)
            # 添加位置价值
            score += self.position_table[row][col][player]

        for piece, row, col in opponent_pieces:
            score -= piece_values.get(piece.rank, 0)
            score -= self.position_table[row][col][opponent]

        # 3. 棋子数量优势
        score += (len(my_pieces) - len(opponent_pieces)) * 50

        # 4. 兽穴控制
        my_den = game.den_positions[player]
        opponent_den = game.den_positions[opponent]

        # 检查是否有棋子在对方兽穴附近
        for piece, row, col in my_pieces:
            distance_to_opponent_den = abs(row - opponent_den[0]) + abs(col - opponent_den[1])
            if distance_to_opponent_den <= 2:
                score += (3 - distance_to_opponent_den) * 30

        for piece, row, col in opponent_pieces:
            distance_to_my_den = abs(row - my_den[0]) + abs(col - my_den[1])
            if distance_to_my_den <= 2:
                score -= (3 - distance_to_my_den) * 30

        # 5. 棋子安全性
        for piece, row, col in my_pieces:
            danger_score = self._calculate_piece_danger(game, piece, row, col, player)
            score -= danger_score

        for piece, row, col in opponent_pieces:
            danger_score = self._calculate_piece_danger(game, piece, row, col, opponent)
            score += danger_score

        # 6. 陷阱控制
        my_traps = game.trap_positions[player]
        opponent_traps = game.trap_positions[opponent]

        # 检查对方棋子是否在我的陷阱中
        for piece, row, col in opponent_pieces:
            if (row, col) in my_traps:
                score += piece_values.get(piece.rank, 0) * 0.5  # 在陷阱中的棋子价值减半

        # 检查我的棋子是否在对方陷阱中
        for piece, row, col in my_pieces:
            if (row, col) in opponent_traps:
                score -= piece_values.get(piece.rank, 0) * 0.5

        # 7. 河流控制（老鼠）
        my_rats = [p for p in my_pieces if p[0].rank == 1]
        opponent_rats = [p for p in opponent_pieces if p[0].rank == 1]

        river_positions = [
            (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2),
            (3, 4), (3, 5), (4, 4), (4, 5), (5, 4), (5, 5)
        ]

        # 我方老鼠在河流中的优势
        for piece, row, col in my_rats:
            if (row, col) in river_positions:
                score += 30  # 老鼠在河流中有优势

        # 对方老鼠在河流中的威胁
        for piece, row, col in opponent_rats:
            if (row, col) in river_positions:
                score -= 30

        # 8. 高价值棋子的保护
        my_high_value = [p for p in my_pieces if p[0].rank >= 6]
        opponent_high_value = [p for p in opponent_pieces if p[0].rank >= 6]

        # 如果我有高价值棋子而对方没有，加分
        if my_high_value and not opponent_high_value:
            score += 100
        elif not my_high_value and opponent_high_value:
            score -= 100

        # 9. 移动能力（可以移动的棋子数量）
        my_movable_count = len(game.get_valid_moves(player))
        opponent_movable_count = len(game.get_valid_moves(opponent))
        score += (my_movable_count - opponent_movable_count) * 2

        # 10. 狮虎的特殊价值（可以跳河）
        for piece, row, col in my_pieces:
            if piece.rank in [6, 7]:  # 虎、狮
                # 检查是否能跳河
                if self._can_jump_river(game, row, col, player):
                    score += 20

        for piece, row, col in opponent_pieces:
            if piece.rank in [6, 7]:
                if self._can_jump_river(game, row, col, opponent):
                    score -= 20

        # 11. 中局策略（大师级和专业级）
        if self.difficulty in ['master', 'professional']:
            midgame_score = self._evaluate_midgame(game, player, my_pieces, opponent_pieces)
            score += midgame_score

        # 12. 残局技巧（大师级）
        if self.difficulty == 'master':
            endgame_score = self._evaluate_endgame(game, player, my_pieces, opponent_pieces)
            score += endgame_score

        # 13. 棋子协调性（大师级）
        if self.difficulty == 'master':
            coordination_score = self._evaluate_coordination(game, player, my_pieces, opponent_pieces)
            score += coordination_score

        # 14. 高级战术评估（大师级专用）
        if self.difficulty == 'master':
            advanced_tactics_score = self._evaluate_advanced_tactics(game, player, my_pieces, opponent_pieces)
            score += advanced_tactics_score

        # 15. 随机因素（避免AI过于僵化）
        if self.difficulty != 'master':
            score += random.uniform(-5, 5)

        return score

    def _calculate_piece_danger(self, game, piece, row, col, player):
        """计算棋子的危险程度"""
        danger_score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 检查是否有对手的棋子可以吃掉这个棋子
        for other_row in range(9):
            for other_col in range(7):
                other_piece = game.board[other_row][other_col]
                if other_piece and other_piece.player != player:
                    if game.is_valid_move(other_row, other_col, row, col, other_piece.player):
                        # 如果对手能吃掉这个棋子
                        if other_piece.rank >= piece.rank:
                            # 如果在陷阱中，危险更大
                            if game.is_in_opponent_trap(row, col, player):
                                danger_score += piece.rank * 3
                            else:
                                danger_score += piece.rank * 1.5

        return danger_score

    def _can_jump_river(self, game, row, col, player):
        """检查狮虎是否能跳河"""
        piece = game.board[row][col]
        if not piece or piece.rank not in [6, 7]:
            return False

        # 检查四个方向是否可以跳跃
        directions = [
            (4, 0),   # 纵向跳跃
            (-4, 0),
            (0, 3),   # 横向跳跃
            (0, -3)
        ]

        for dr, dc in directions:
            to_row, to_col = row + dr, col + dc
            if 0 <= to_row < 9 and 0 <= to_col < 7:
                if game.is_valid_move(row, col, to_row, to_col, player):
                    return True

        return False

    def _evaluate_opening(self, game, player, my_pieces, opponent_pieces):
        """评估开局策略（大师级和专业级）"""
        score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 判断是否是开局阶段（双方棋子都在初始位置附近）
        total_pieces = len(my_pieces) + len(opponent_pieces)
        if total_pieces < 14:  # 少于14个棋子，说明已经过了开局阶段
            return 0

        # 开局原则：
        # 1. 控制中心
        center_positions = [(4, 3), (4, 2), (4, 4), (3, 3), (5, 3)]
        for piece, row, col in my_pieces:
            if (row, col) in center_positions:
                score += 15

        # 2. 快速出子（特别是狮子和老虎）
        lion_and_tiger = [p for p in my_pieces if p[0].rank in [6, 7]]
        for piece, row, col in lion_and_tiger:
            # 如果狮子和老虎已经离开了初始位置
            initial_row = 0 if player == 'red' else 8
            if abs(row - initial_row) > 1:
                score += 20

        # 3. 老鼠灵活运用
        my_rats = [p for p in my_pieces if p[0].rank == 1]
        for piece, row, col in my_rats:
            # 老鼠应该靠近河流
            river_positions = [
                (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2),
                (3, 4), (3, 5), (4, 4), (4, 5), (5, 4), (5, 5)
            ]
            for river_pos in river_positions:
                if abs(row - river_pos[0]) + abs(col - river_pos[1]) <= 2:
                    score += 10
                    break

        # 4. 避免过早暴露高价值棋子
        my_high_value = [p for p in my_pieces if p[0].rank >= 6]
        for piece, row, col in my_high_value:
            opponent_den = game.den_positions[opponent]
            distance_to_enemy_den = abs(row - opponent_den[0]) + abs(col - opponent_den[1])
            # 如果高价值棋子过于靠近对方兽穴，扣分
            if distance_to_enemy_den < 4:
                score -= 15

        # 5. 保护自己的兽穴
        my_den = game.den_positions[player]
        for piece, row, col in my_pieces:
            distance_to_my_den = abs(row - my_den[0]) + abs(col - my_den[1])
            if distance_to_my_den <= 2 and piece.rank >= 5:
                score += 20  # 高价值棋子保护兽穴

        return score

    def _evaluate_midgame(self, game, player, my_pieces, opponent_pieces):
        """评估中局策略（大师级和专业级）"""
        score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 判断是否是中局阶段
        total_pieces = len(my_pieces) + len(opponent_pieces)
        if total_pieces > 12:  # 棋子过多，还在开局阶段
            return 0
        if total_pieces < 8:   # 棋子过少，已经进入残局
            return 0

        # 中局原则：
        # 1. 集中优势兵力
        my_power = sum(p[0].rank for p in my_pieces)
        opponent_power = sum(p[0].rank for p in opponent_pieces)
        if my_power > opponent_power * 1.2:
            score += 50  # 主动进攻
        elif my_power < opponent_power * 0.8:
            score -= 30  # 需要防守

        # 2. 控制关键位置
        key_positions = [
            (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),  # 中路
            (3, 1), (3, 5), (5, 1), (5, 5)           # 河流边缘
        ]
        for piece, row, col in my_pieces:
            if (row, col) in key_positions:
                score += 10

        # 3. 利用狮虎跳河优势
        my_lion_tiger = [p for p in my_pieces if p[0].rank in [6, 7]]
        for piece, row, col in my_lion_tiger:
            if self._can_jump_river(game, row, col, player):
                opponent_den = game.den_positions[opponent]
                distance_to_den = abs(row - opponent_den[0]) + abs(col - opponent_den[1])
                # 如果能跳河并且靠近对方兽穴，加分
                if distance_to_den < 6:
                    score += 25

        # 4. 老鼠的战略价值
        my_rats = [p for p in my_pieces if p[0].rank == 1]
        opponent_elephants = [p for p in opponent_pieces if p[0].rank == 8]

        # 如果我有老鼠而对方有大象，老鼠的价值提升
        if my_rats and opponent_elephants:
            for piece, row, col in my_rats:
                # 老鼠应该靠近大象
                for elephant in opponent_elephants:
                    distance = abs(row - elephant[1]) + abs(col - elephant[2])
                    if distance < 5:
                        score += 30

        # 5. 保护高价值棋子
        my_high_value = [p for p in my_pieces if p[0].rank >= 6]
        for piece, row, col in my_high_value:
            # 检查这个棋子是否被保护
            protected = False
            for other_piece, other_row, other_col in my_pieces:
                if other_piece.rank >= piece.rank and (other_row, other_col) != (row, col):
                    # 检查这个棋子是否能支援
                    if abs(other_row - row) + abs(other_col - col) <= 2:
                        protected = True
                        break
            if protected:
                score += 15

        # 6. 陷阱利用
        my_traps = game.trap_positions[player]
        opponent_in_traps = 0
        for piece, row, col in opponent_pieces:
            if (row, col) in my_traps:
                opponent_in_traps += 1
        score += opponent_in_traps * 40

        return score

    def _evaluate_endgame(self, game, player, my_pieces, opponent_pieces):
        """评估残局技巧（大师级）"""
        score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 判断是否是残局阶段
        total_pieces = len(my_pieces) + len(opponent_pieces)
        if total_pieces >= 8:  # 棋子过多，还没有进入残局
            return 0

        # 残局原则：
        # 1. 棋子数量优势
        score += (len(my_pieces) - len(opponent_pieces)) * 100

        # 2. 高价值棋子优势
        my_high_value = sum(p[0].rank for p in my_pieces)
        opponent_high_value = sum(p[0].rank for p in opponent_pieces)
        score += (my_high_value - opponent_high_value) * 10

        # 3. 老鼠的特殊作用（吃象）
        my_rats = [p for p in my_pieces if p[0].rank == 1]
        opponent_elephants = [p for p in opponent_pieces if p[0].rank == 8]

        if my_rats and not opponent_elephants:
            score += 200  # 我有老鼠对方没有象，优势巨大
        elif not my_rats and opponent_elephants:
            score -= 200  # 对方有象我没有老鼠，劣势巨大

        # 4. 狮虎的机动性优势
        my_lion_tiger = [p for p in my_pieces if p[0].rank in [6, 7]]
        opponent_lion_tiger = [p for p in opponent_pieces if p[0].rank in [6, 7]]

        if my_lion_tiger and not opponent_lion_tiger:
            score += 150
        elif not my_lion_tiger and opponent_lion_tiger:
            score -= 150

        # 5. 兽穴距离
        opponent_den = game.den_positions[opponent]
        my_den = game.den_positions[player]

        # 我方棋子到对方兽穴的最短距离
        my_min_distance = min(
            abs(row - opponent_den[0]) + abs(col - opponent_den[1])
            for piece, row, col in my_pieces
        ) if my_pieces else 100

        # 对方棋子到我方兽穴的最短距离
        opponent_min_distance = min(
            abs(row - my_den[0]) + abs(col - my_den[1])
            for piece, row, col in opponent_pieces
        ) if opponent_pieces else 100

        score += (opponent_min_distance - my_min_distance) * 20

        # 6. 检查是否即将获胜
        for piece, row, col in my_pieces:
            if (row, col) == opponent_den:
                score += 1000  # 即将获胜
            elif abs(row - opponent_den[0]) + abs(col - opponent_den[1]) == 1:
                score += 500  # 下一步即可进入兽穴

        # 7. 检查是否即将失败
        for piece, row, col in opponent_pieces:
            if (row, col) == my_den:
                score -= 1000  # 即将失败
            elif abs(row - my_den[0]) + abs(col - my_den[1]) == 1:
                score -= 500  # 对方下一步即可进入兽穴

        # 8. 棋子的可移动性
        my_movable_count = len(game.get_valid_moves(player))
        opponent_movable_count = len(game.get_valid_moves(opponent))
        score += (my_movable_count - opponent_movable_count) * 5

        return score

    def _evaluate_coordination(self, game, player, my_pieces, opponent_pieces):
        """评估棋子协调性（大师级）"""
        score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 1. 棋子间的相互保护
        for piece, row, col in my_pieces:
            protected = 0
            for other_piece, other_row, other_col in my_pieces:
                if other_piece.rank >= piece.rank and (other_row, other_col) != (row, col):
                    distance = abs(other_row - row) + abs(other_col - col)
                    if distance <= 2:
                        protected += 1
            score += protected * 5

        # 2. 棋子间的相互威胁
        my_threats = 0
        opponent_threats = 0

        for piece, row, col in my_pieces:
            for other_piece, other_row, other_col in opponent_pieces:
                if game.is_valid_move(row, col, other_row, other_col, player):
                    if piece.rank >= other_piece.rank:
                        my_threats += 1

        for piece, row, col in opponent_pieces:
            for other_piece, other_row, other_col in my_pieces:
                if game.is_valid_move(row, col, other_row, other_col, opponent):
                    if piece.rank >= other_piece.rank:
                        opponent_threats += 1

        score += (my_threats - opponent_threats) * 10

        # 3. 棋子的集中度（避免过于分散）
        if len(my_pieces) > 0:
            avg_row = sum(row for piece, row, col in my_pieces) / len(my_pieces)
            avg_col = sum(col for piece, row, col in my_pieces) / len(my_pieces)

            spread = sum(
                abs(row - avg_row) + abs(col - avg_col)
                for piece, row, col in my_pieces
            )

            # 适度的集中是好的，但过于集中也不好
            if spread < 10:
                score += 20  # 集中度好
            elif spread > 25:
                score -= 20  # 过于分散

        # 4. 关键位置的协同防守
        my_den = game.den_positions[player]
        den_defenders = 0
        for piece, row, col in my_pieces:
            if abs(row - my_den[0]) + abs(col - my_den[1]) <= 2:
                den_defenders += 1
        score += den_defenders * 10

        # 5. 河流的控制协同
        river_positions = [
            (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2),
            (3, 4), (3, 5), (4, 4), (4, 5), (5, 4), (5, 5)
        ]

        my_river_control = 0
        opponent_river_control = 0

        for piece, row, col in my_pieces:
            if (row, col) in river_positions:
                my_river_control += 1
            else:
                # 检查是否能威胁到河流
                for river_pos in river_positions:
                    if abs(row - river_pos[0]) + abs(col - river_pos[1]) <= 2:
                        my_river_control += 0.5
                        break

        for piece, row, col in opponent_pieces:
            if (row, col) in river_positions:
                opponent_river_control += 1
            else:
                for river_pos in river_positions:
                    if abs(row - river_pos[0]) + abs(col - river_pos[1]) <= 2:
                        opponent_river_control += 0.5
                        break

        score += (my_river_control - opponent_river_control) * 15

        return score

    def _evaluate_advanced_tactics(self, game, player, my_pieces, opponent_pieces):
        """评估高级战术（大师级专用）"""
        score = 0
        opponent = 'blue' if player == 'red' else 'red'

        # 1. 预测性吃子 - 评估能否在下几步吃掉高价值棋子
        for piece, row, col in my_pieces:
            for opp_piece, opp_row, opp_col in opponent_pieces:
                if piece.rank >= opp_piece.rank:
                    # 检查能否直接吃掉
                    if game.is_valid_move(row, col, opp_row, opp_col, player):
                        # 计算吃掉的价值
                        capture_value = opp_piece.rank * 20
                        # 如果对方棋子在陷阱中，价值更高
                        if (opp_row, opp_col) in game.trap_positions[player]:
                            capture_value *= 1.5
                        score += capture_value

        # 2. 威胁链评估 - 检查是否能形成连续威胁
        threat_chain = 0
        for piece, row, col in my_pieces:
            threatened_pieces = []
            for opp_piece, opp_row, opp_col in opponent_pieces:
                if piece.rank >= opp_piece.rank and game.is_valid_move(row, col, opp_row, opp_col, player):
                    threatened_pieces.append(opp_piece)
            # 如果一个棋子能威胁多个对方棋子，加分
            if len(threatened_pieces) > 1:
                threat_chain += len(threatened_pieces) * 15
            # 如果能威胁高价值棋子，加分更多
            for opp_piece in threatened_pieces:
                if opp_piece.rank >= 6:
                    threat_chain += 25
        score += threat_chain

        # 3. 陷阱战术 - 评估能否将对方棋子引入陷阱
        my_traps = game.trap_positions[player]
        for trap_pos in my_traps:
            trap_row, trap_col = trap_pos
            # 检查是否有棋子能保护这个陷阱
            protectors = 0
            for piece, row, col in my_pieces:
                if abs(row - trap_row) + abs(col - trap_col) <= 2:
                    protectors += 1
            if protectors > 0:
                score += protectors * 10

        # 4. 兽穴突破 - 评估进入对方兽穴的可能性
        opponent_den = game.den_positions[opponent]
        den_distance_bonus = 0
        for piece, row, col in my_pieces:
            distance = abs(row - opponent_den[0]) + abs(col - opponent_den[1])
            if distance <= 3:
                # 越近奖励越高
                den_distance_bonus += (4 - distance) * 30
                # 如果是高价值棋子，奖励更高
                if piece.rank >= 6:
                    den_distance_bonus += (4 - distance) * 20
        score += den_distance_bonus

        # 5. 老鼠象相克策略
        my_rats = [p for p in my_pieces if p[0].rank == 1]
        opponent_elephants = [p for p in opponent_pieces if p[0].rank == 8]

        if my_rats and opponent_elephants:
            for rat in my_rats:
                for elephant in opponent_elephants:
                    distance = abs(rat[1] - elephant[1]) + abs(rat[2] - elephant[2])
                    if distance <= 3:
                        score += 50  # 老鼠接近大象，战术优势
                    elif distance <= 5:
                        score += 30

        # 6. 狮虎跳河战术
        jumping_pieces = []
        for piece, row, col in my_pieces:
            if piece.rank in [6, 7] and self._can_jump_river(game, row, col, player):
                jumping_pieces.append((piece, row, col))

        for piece, row, col in jumping_pieces:
            # 评估跳河后的价值
            directions = [(4, 0), (-4, 0), (0, 3), (0, -3)]
            for dr, dc in directions:
                to_row, to_col = row + dr, col + dc
                if 0 <= to_row < 9 and 0 <= to_col < 7:
                    if game.is_valid_move(row, col, to_row, to_col, player):
                        # 跳河后的位置价值
                        distance_to_den = abs(to_row - opponent_den[0]) + abs(to_col - opponent_den[1])
                        score += (12 - distance_to_den) * 15

        # 7. 棋子牺牲评估 - 有时牺牲小棋子换取优势
        sacrifice_value = 0
        for piece, row, col in my_pieces:
            if piece.rank <= 3:  # 小棋子
                # 检查牺牲这个棋子能否保护高价值棋子
                for high_piece, high_row, high_col in my_pieces:
                    if high_piece.rank >= 6:
                        distance = abs(row - high_row) + abs(col - high_col)
                        if distance <= 2:
                            sacrifice_value += 20
        score += sacrifice_value

        # 8. 反向思考 - 评估对手的最佳移动并阻止
        opponent_best_threat = 0
        for opp_piece, opp_row, opp_col in opponent_pieces:
            for my_piece, my_row, my_col in my_pieces:
                if opp_piece.rank >= my_piece.rank:
                    if game.is_valid_move(opp_row, opp_col, my_row, my_col, opponent):
                        # 对手能吃掉我的棋子，这是威胁
                        threat_value = my_piece.rank * 15
                        # 如果我的高价值棋子受威胁，威胁更大
                        if my_piece.rank >= 6:
                            threat_value *= 1.5
                        opponent_best_threat += threat_value
        score -= opponent_best_threat * 0.8  # 扣分表示需要防守

        # 9. 关键路径控制 - 控制通往兽穴的关键路径
        key_paths = []
        if player == 'red':
            # 红方向下进攻
            for col in [2, 3, 4]:  # 中间三列
                for row in range(6, 9):
                    key_paths.append((row, col))
        else:
            # 蓝方向上进攻
            for col in [2, 3, 4]:
                for row in range(0, 3):
                    key_paths.append((row, col))

        path_control = 0
        for piece, row, col in my_pieces:
            if (row, col) in key_paths:
                path_control += 15
        score += path_control

        # 10. 时间压力 - 评估是否需要快速进攻或防守
        my_piece_count = len(my_pieces)
        opponent_piece_count = len(opponent_pieces)

        if my_piece_count > opponent_piece_count + 2:
            # 我方有明显优势，可以更激进
            score += 100
        elif opponent_piece_count > my_piece_count + 2:
            # 对方有明显优势，需要防守
            score -= 100

        return score
