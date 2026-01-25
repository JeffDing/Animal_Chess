#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全面测试斗兽棋规则"""

from game_logic import DoushouqiGame, Piece

def test_lion_tiger_jump_river():
    """测试狮子老虎跳河"""
    print("=== 测试狮子老虎跳河 ===")

    game = DoushouqiGame()
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 测试1：狮子在河边，可以跳过河
    game.board[2][1] = Piece('狮', 7, 'red')  # 红方狮子在河边
    can_jump = game.is_valid_move(2, 1, 6, 1, 'red')
    print(f"狮子从(2,1)跳到(6,1)（跳过河）: {'✓ 正确' if can_jump else '✗ 错误'}")

    # 测试2：河中有老鼠阻挡，不能跳
    game.board[4][1] = Piece('鼠', 1, 'blue')  # 蓝方老鼠在河中
    can_jump = game.is_valid_move(2, 1, 6, 1, 'red')
    print(f"河中有老鼠阻挡，狮子不能跳: {'✓ 正确' if not can_jump else '✗ 错误'}")

    # 测试3：河对岸有比狮子强的棋子，不能跳
    game.board[4][1] = None  # 清除老鼠
    game.board[6][1] = Piece('象', 8, 'blue')  # 蓝方大象在河对岸
    can_jump = game.is_valid_move(2, 1, 6, 1, 'red')
    print(f"河对岸有大象（比狮子强），不能跳: {'✓ 正确' if not can_jump else '✗ 错误'}")

    # 测试4：河对岸有比狮子弱的棋子，可以跳并吃掉
    game.board[6][1] = Piece('狗', 3, 'blue')  # 蓝方狗在河对岸
    can_jump = game.is_valid_move(2, 1, 6, 1, 'red')
    print(f"河对岸有狗（比狮子弱），可以跳并吃掉: {'✓ 正确' if can_jump else '✗ 错误'}")

    # 测试5：横向跳河
    game.board = [[None for _ in range(7)] for _ in range(9)]
    game.board[4][0] = Piece('虎', 6, 'red')  # 红方老虎在河边
    can_jump = game.is_valid_move(4, 0, 4, 3, 'red')
    print(f"老虎从(4,0)横向跳到(4,3)（跳过河）: {'✓ 正确' if can_jump else '✗ 错误'}")

def test_rat_in_river():
    """测试老鼠入河"""
    print("\n=== 测试老鼠入河 ===")

    game = DoushouqiGame()
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 测试1：老鼠可以入河
    game.board[2][1] = Piece('鼠', 1, 'red')
    can_enter = game.is_valid_move(2, 1, 3, 1, 'red')
    print(f"老鼠可以入河: {'✓ 正确' if can_enter else '✗ 错误'}")

    # 测试2：老鼠在河中可以移动
    game.board[3][1] = Piece('鼠', 1, 'red')
    can_move = game.is_valid_move(3, 1, 4, 1, 'red')
    print(f"老鼠在河中可以移动: {'✓ 正确' if can_move else '✗ 错误'}")

    # 测试3：老鼠在河中不能被其他棋子吃掉
    game.board[3][1] = Piece('鼠', 1, 'red')
    game.board[2][1] = Piece('象', 8, 'blue')  # 蓝方大象在河边
    can_capture = game.is_valid_move(2, 1, 3, 1, 'blue')
    print(f"大象不能吃河中的老鼠: {'✓ 正确' if not can_capture else '✗ 错误'}")

    # 测试4：老鼠在河中不能吃大象
    game.board[3][1] = Piece('鼠', 1, 'red')
    game.board[4][1] = Piece('象', 8, 'blue')  # 蓝方大象在河边
    can_capture = game.is_valid_move(3, 1, 4, 1, 'red')
    print(f"河中的老鼠不能吃大象: {'✓ 正确' if not can_capture else '✗ 错误'}")

    # 测试5：老鼠在河中不能吃岸上的任何棋子（包括老鼠）
    game.board[3][1] = Piece('鼠', 1, 'red')
    game.board[2][1] = Piece('鼠', 1, 'blue')  # 蓝方老鼠在岸边
    can_capture = game.is_valid_move(3, 1, 2, 1, 'red')
    print(f"河中的老鼠不能吃岸上的老鼠（符合规则）: {'✓ 正确' if not can_capture else '✗ 错误'}")

    # 测试6：两只老鼠在河内相遇，可以相互进食
    game.board[3][1] = Piece('鼠', 1, 'red')
    game.board[3][2] = Piece('鼠', 1, 'blue')  # 两只老鼠都在河中
    can_capture = game.is_valid_move(3, 1, 3, 2, 'red')
    print(f"两只老鼠在河内相遇可以相互进食: {'✓ 正确' if can_capture else '✗ 错误'}")

    # 测试7：老鼠从河中上岸后不能吃大象（规则：老鼠在河中不能吃岸上的任何棋子）
    game.board[3][1] = Piece('鼠', 1, 'red')
    game.board[2][1] = Piece('象', 8, 'blue')  # 蓝方大象在岸边
    can_capture = game.is_valid_move(3, 1, 2, 1, 'red')
    print(f"老鼠从河中上岸后不能吃大象: {'✓ 正确' if not can_capture else '✗ 错误'}")

def test_mutual_capture():
    """测试互食规则"""
    print("\n=== 测试互食规则 ===")

    # 测试1：同级棋子可以互吃
    lion1 = Piece('狮', 7, 'red')
    lion2 = Piece('狮', 7, 'blue')
    can_capture = lion1.can_capture(lion2, other_in_trap=False, self_in_river=False, other_in_river=False)
    print(f"红方狮子可以吃蓝方狮子（同级）: {'✓ 正确' if can_capture else '✗ 错误'}")

    # 测试2：老虎(6)可以吃狮子(7)不可以
    tiger = Piece('虎', 6, 'red')
    lion = Piece('狮', 7, 'blue')
    can_capture = tiger.can_capture(lion, other_in_trap=False, self_in_river=False, other_in_river=False)
    print(f"老虎(6)不能吃狮子(7): {'✓ 正确' if not can_capture else '✗ 错误'}")

    # 测试3：狮子(7)可以吃老虎(6)可以
    can_capture = lion.can_capture(tiger, other_in_trap=False, self_in_river=False, other_in_river=False)
    print(f"狮子(7)可以吃老虎(6): {'✓ 正确' if can_capture else '✗ 错误'}")

def test_trap_rules():
    """测试陷阱规则"""
    print("\n=== 测试陷阱规则 ===")

    game = DoushouqiGame()
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 测试1：棋子可以进入自己的陷阱
    game.board[1][2] = Piece('鼠', 1, 'red')
    can_enter = game.is_valid_move(1, 2, 0, 2, 'red')
    print(f"红方棋子可以进入红方陷阱: {'✓ 正确' if can_enter else '✗ 错误'}")

    # 测试2：棋子可以进入对方的陷阱
    game.board[1][2] = Piece('鼠', 1, 'blue')
    can_enter = game.is_valid_move(1, 2, 0, 2, 'blue')
    print(f"蓝方棋子可以进入红方陷阱: {'✓ 正确' if can_enter else '✗ 错误'}")

    # 测试3：棋子在自己的陷阱中，对方不能吃掉
    game.board[0][2] = Piece('鼠', 1, 'red')  # 红方老鼠在红方陷阱中
    game.board[0][1] = Piece('象', 8, 'blue')  # 蓝方大象在旁边
    can_capture = game.is_valid_move(0, 1, 0, 2, 'blue')
    print(f"蓝方大象不能吃红方陷阱中的红方老鼠: {'✓ 正确' if not can_capture else '✗ 错误'}")

    # 测试4：棋子在对方的陷阱中，对方任意棋子都可以吃掉
    game.board[0][2] = Piece('象', 8, 'blue')  # 蓝方大象在红方陷阱中
    game.board[0][1] = Piece('鼠', 1, 'red')  # 红方老鼠在旁边
    can_capture = game.is_valid_move(0, 1, 0, 2, 'red')
    print(f"红方老鼠可以吃红方陷阱中的蓝方大象: {'✓ 正确' if can_capture else '✗ 错误'}")

    # 测试5：棋子在对方的陷阱中，对方低等级棋子也可以吃掉高等级棋子
    game.board[0][2] = Piece('象', 8, 'blue')  # 蓝方大象在红方陷阱中
    game.board[0][1] = Piece('猫', 2, 'red')  # 红方猫在旁边
    can_capture = game.is_valid_move(0, 1, 0, 2, 'red')
    print(f"红方猫可以吃红方陷阱中的蓝方大象: {'✓ 正确' if can_capture else '✗ 错误'}")

    # 测试6：棋子可以从自己的陷阱中走出来
    game = DoushouqiGame()
    game.board = [[None for _ in range(7)] for _ in range(9)]
    game.board[0][2] = Piece('鼠', 1, 'red')  # 红方老鼠在红方陷阱中
    can_move = game.is_valid_move(0, 2, 0, 1, 'red')
    print(f"棋子可以从自己的陷阱中走出来: {'✓ 正确' if can_move else '✗ 错误'}")

    # 测试7：棋子可以从对方的陷阱中走出来
    game = DoushouqiGame()
    game.board = [[None for _ in range(7)] for _ in range(9)]
    game.board[0][2] = Piece('鼠', 1, 'blue')  # 蓝方老鼠在红方陷阱中
    can_move = game.is_valid_move(0, 2, 0, 1, 'blue')
    print(f"棋子可以从对方的陷阱中走出来: {'✓ 正确' if can_move else '✗ 错误'}")

def test_rat_eat_elephant():
    """测试老鼠吃大象"""
    print("\n=== 测试老鼠吃大象 ===")

    # 测试1：老鼠在陆地上可以吃大象
    rat = Piece('鼠', 1, 'red')
    elephant = Piece('象', 8, 'blue')
    can_capture = rat.can_capture(elephant, other_in_trap=False, self_in_river=False, other_in_river=False)
    print(f"老鼠在陆地上可以吃大象: {'✓ 正确' if can_capture else '✗ 错误'}")

    # 测试2：老鼠在河中不能吃大象
    can_capture = rat.can_capture(elephant, other_in_trap=False, self_in_river=True, other_in_river=False)
    print(f"老鼠在河中不能吃大象: {'✓ 正确' if not can_capture else '✗ 错误'}")

    # 测试3：大象可以吃老鼠
    can_capture = elephant.can_capture(rat, other_in_trap=False, self_in_river=False, other_in_river=False)
    print(f"大象可以吃老鼠: {'✓ 正确' if can_capture else '✗ 错误'}")

def test_cannot_enter_own_den():
    """测试不能进入自己的兽穴"""
    print("\n=== 测试不能进入自己的兽穴 ===")

    game = DoushouqiGame()
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 测试1：红方棋子不能进入红方兽穴
    game.board[1][3] = Piece('鼠', 1, 'red')
    can_enter = game.is_valid_move(1, 3, 0, 3, 'red')
    print(f"红方棋子不能进入红方兽穴: {'✓ 正确' if not can_enter else '✗ 错误'}")

    # 测试2：蓝方棋子不能进入蓝方兽穴
    game.board[7][3] = Piece('鼠', 1, 'blue')
    can_enter = game.is_valid_move(7, 3, 8, 3, 'blue')
    print(f"蓝方棋子不能进入蓝方兽穴: {'✓ 正确' if not can_enter else '✗ 错误'}")

    # 测试3：红方棋子可以进入蓝方兽穴
    game.board[7][3] = Piece('鼠', 1, 'red')
    can_enter = game.is_valid_move(7, 3, 8, 3, 'red')
    print(f"红方棋子可以进入蓝方兽穴: {'✓ 正确' if can_enter else '✗ 错误'}")

def test_other_pieces_cannot_enter_river():
    """测试其他棋子不能入河"""
    print("\n=== 测试其他棋子不能入河 ===")

    game = DoushouqiGame()
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 测试1：象不能入河
    game.board[2][1] = Piece('象', 8, 'red')
    can_enter = game.is_valid_move(2, 1, 3, 1, 'red')
    print(f"象不能入河: {'✓ 正确' if not can_enter else '✗ 错误'}")

    # 测试2：狮不能入河
    game.board[2][1] = Piece('狮', 7, 'red')
    can_enter = game.is_valid_move(2, 1, 3, 1, 'red')
    print(f"狮不能入河: {'✓ 正确' if not can_enter else '✗ 错误'}")

    # 测试3：虎不能入河
    game.board[2][1] = Piece('虎', 6, 'red')
    can_enter = game.is_valid_move(2, 1, 3, 1, 'red')
    print(f"虎不能入河: {'✓ 正确' if not can_enter else '✗ 错误'}")

def test_red_moves_first():
    """测试红方先行"""
    print("\n=== 测试红方先行 ===")

    game = DoushouqiGame()
    print(f"当前玩家: {game.current_player}")
    print(f"红方先行: {'✓ 正确' if game.current_player == 'red' else '✗ 错误'}")

if __name__ == "__main__":
    try:
        test_lion_tiger_jump_river()
        test_rat_in_river()
        test_mutual_capture()
        test_trap_rules()
        test_rat_eat_elephant()
        test_cannot_enter_own_den()
        test_other_pieces_cannot_enter_river()
        test_red_moves_first()
        print("\n✅ 所有规则测试完成！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
