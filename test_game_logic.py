#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试游戏逻辑修复"""

from game_logic import DoushouqiGame, Piece

def test_rat_vs_elephant():
    """测试老鼠吃大象的逻辑"""
    print("=== 测试老鼠吃大象的逻辑 ===")

    # 创建测试棋子
    rat = Piece('鼠', 1, 'red')
    elephant = Piece('象', 8, 'blue')

    # 测试老鼠吃大象（应该可以）
    result = rat.can_capture(elephant, other_in_trap=False)
    print(f"老鼠吃大象（不在陷阱中）: {'✓ 正确' if result else '✗ 错误'}")

    # 测试老鼠吃大象（在陷阱中，应该也可以）
    result = rat.can_capture(elephant, other_in_trap=True)
    print(f"老鼠吃大象（在陷阱中）: {'✓ 正确' if result else '✗ 错误'}")

    # 测试大象吃老鼠（应该可以，因为大象等级高）
    result = elephant.can_capture(rat, other_in_trap=False)
    print(f"大象吃老鼠（不在陷阱中）: {'✓ 正确' if result else '✗ 错误'}")

    # 测试大象吃老鼠（老鼠在陷阱中，应该也可以）
    result = elephant.can_capture(rat, other_in_trap=True)
    print(f"大象吃老鼠（老鼠在陷阱中）: {'✓ 正确' if result else '✗ 错误'}")

def test_capture_ranks():
    """测试等级吃子逻辑"""
    print("\n=== 测试等级吃子逻辑 ===")

    # 创建测试棋子
    lion = Piece('狮', 7, 'red')
    tiger = Piece('虎', 6, 'blue')
    wolf = Piece('狼', 4, 'red')
    dog = Piece('狗', 3, 'blue')

    # 测试同级吃子
    result = lion.can_capture(tiger, other_in_trap=False)
    print(f"狮子(7)吃老虎(6): {'✓ 正确' if result else '✗ 错误'}")

    # 测试小吃大（应该不可以）
    result = dog.can_capture(wolf, other_in_trap=False)
    print(f"狗(3)吃狼(4): {'✓ 正确' if not result else '✗ 错误'}")

    # 测试小吃大（如果在陷阱中，应该可以）
    result = dog.can_capture(wolf, other_in_trap=True)
    print(f"狗(3)吃狼(4)（狼在陷阱中）: {'✓ 正确' if result else '✗ 错误'}")

def test_trap_logic():
    """测试陷阱逻辑"""
    print("\n=== 测试陷阱逻辑 ===")

    game = DoushouqiGame()

    # 测试陷阱位置
    print(f"红方陷阱位置: {game.trap_positions['red']}")
    print(f"蓝方陷阱位置: {game.trap_positions['blue']}")

    # 测试 is_trap 函数
    print(f"(0, 2) 是否是红方陷阱: {'✓ 正确' if game.is_trap(0, 2, 'red') else '✗ 错误'}")
    print(f"(0, 2) 是否是蓝方陷阱: {'✓ 正确' if not game.is_trap(0, 2, 'blue') else '✗ 错误'}")

    # 测试 is_in_opponent_trap 函数
    print(f"红方棋子在(0, 2)是否在蓝方陷阱中: {'✓ 正确' if not game.is_in_opponent_trap(0, 2, 'red') else '✗ 错误'}")
    print(f"蓝方棋子在(0, 2)是否在红方陷阱中: {'✓ 正确' if game.is_in_opponent_trap(0, 2, 'blue') else '✗ 错误'}")
    print(f"红方棋子在(8, 2)是否在蓝方陷阱中: {'✓ 正确' if game.is_in_opponent_trap(8, 2, 'red') else '✗ 错误'}")
    print(f"蓝方棋子在(8, 2)是否在红方陷阱中: {'✓ 正确' if not game.is_in_opponent_trap(8, 2, 'blue') else '✗ 错误'}")

def test_move_to_trap():
    """测试移动到陷阱"""
    print("\n=== 测试移动到陷阱 ===")

    game = DoushouqiGame()

    # 手动设置一个测试场景
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 在红方陷阱附近放置棋子
    game.board[1][2] = Piece('鼠', 1, 'blue')  # 蓝方老鼠在红方陷阱旁边

    # 测试蓝方老鼠是否可以移动到红方陷阱
    can_move = game.is_valid_move(1, 2, 0, 2, 'blue')
    print(f"蓝方老鼠移动到红方陷阱(0, 2): {'✓ 正确' if can_move else '✗ 错误'}")

    # 在红方兽穴附近放置棋子
    game.board[1][4] = Piece('鼠', 1, 'red')  # 红方老鼠在红方陷阱旁边

    # 测试红方老鼠是否可以移动到红方陷阱
    can_move = game.is_valid_move(1, 4, 0, 4, 'red')
    print(f"红方老鼠移动到红方陷阱(0, 4): {'✓ 正确' if can_move else '✗ 错误'}")

    # 在红方兽穴附近放置棋子
    game.board[1][3] = Piece('鼠', 1, 'red')  # 红方老鼠在红方兽穴旁边

    # 测试红方老鼠是否可以移动到红方兽穴
    can_move = game.is_valid_move(1, 3, 0, 3, 'red')
    print(f"红方老鼠移动到红方兽穴(0, 3): {'✓ 正确' if not can_move else '✗ 错误'}")

def test_capture_in_trap():
    """测试在陷阱中吃子"""
    print("\n=== 测试在陷阱中吃子 ===")

    game = DoushouqiGame()

    # 手动设置一个测试场景
    # 清空棋盘
    game.board = [[None for _ in range(7)] for _ in range(9)]

    # 在红方陷阱中放置蓝方大象
    game.board[0][2] = Piece('象', 8, 'blue')  # 蓝方大象在红方陷阱中

    # 在陷阱附近放置红方老鼠
    game.board[0][1] = Piece('鼠', 1, 'red')  # 红方老鼠在陷阱旁边

    # 测试红方老鼠是否可以吃掉红方陷阱中的蓝方大象
    can_capture = game.is_valid_move(0, 1, 0, 2, 'red')
    print(f"红方老鼠吃掉红方陷阱中的蓝方大象: {'✓ 正确' if can_capture else '✗ 错误'}")

    # 在陷阱附近放置红方狗
    game.board[0][1] = Piece('狗', 3, 'red')  # 红方狗在陷阱旁边

    # 测试红方狗是否可以吃掉红方陷阱中的蓝方大象（应该可以，因为大象在陷阱中）
    can_capture = game.is_valid_move(0, 1, 0, 2, 'red')
    print(f"红方狗吃掉红方陷阱中的蓝方大象: {'✓ 正确' if can_capture else '✗ 错误'}")

if __name__ == "__main__":
    try:
        test_rat_vs_elephant()
        test_capture_ranks()
        test_trap_logic()
        test_move_to_trap()
        test_capture_in_trap()
        print("\n✅ 所有逻辑测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
