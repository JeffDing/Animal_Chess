import requests
import time

BASE_URL = "http://localhost:5000"

def test_ai_vs_ai_mode():
    """测试AI对战模式"""
    print("=== 测试AI对战模式 ===")

    # 初始化游戏
    response = requests.post(f"{BASE_URL}/api/new_game", json={"mode": "aivai"})
    data = response.json()
    print(f"游戏初始化: gameMode={data['gameMode']}, currentPlayer={data['currentPlayer']}")

    move_count = 0
    max_moves = 10  # 限制测试步数

    while not data['gameOver'] and move_count < max_moves:
        print(f"\n回合 {move_count + 1}: {data['currentPlayer']}方")

        # AI移动
        response = requests.post(f"{BASE_URL}/api/ai_move", json={
            "player": data['currentPlayer'],
            "mode": data['gameMode']
        })
        ai_data = response.json()

        # 检查是否返回了gameOver（AI无路可走的情况）
        if 'gameOver' in ai_data and ai_data['gameOver']:
            print(f"AI无路可走，游戏结束！获胜者: {ai_data['winner']}")
            break

        if ai_data['move']:
            print(f"AI移动: ({ai_data['move']['fromRow']}, {ai_data['move']['fromCol']}) -> ({ai_data['move']['toRow']}, {ai_data['move']['toCol']})")

            # 执行移动
            response = requests.post(f"{BASE_URL}/api/move", json={
                "fromRow": ai_data['move']['fromRow'],
                "fromCol": ai_data['move']['fromCol'],
                "toRow": ai_data['move']['toRow'],
                "toCol": ai_data['move']['toCol'],
                "mode": data['gameMode']
            })
            data = response.json()

            print(f"移动后: currentPlayer={data['currentPlayer']}, gameOver={data['gameOver']}")

            if data['gameOver']:
                print(f"游戏结束！获胜者: {data['winner']}")
                break
        else:
            print("AI无法移动")
            break

        move_count += 1
        time.sleep(0.5)  # 模拟延迟

    print(f"\n测试完成，共进行了 {move_count} 步")

def test_pve_mode():
    """测试人机对战模式"""
    print("\n=== 测试人机对战模式 ===")

    # 初始化游戏
    response = requests.post(f"{BASE_URL}/api/new_game", json={"mode": "pve"})
    data = response.json()
    print(f"游戏初始化: gameMode={data['gameMode']}, currentPlayer={data['currentPlayer']}")

    move_count = 0
    max_moves = 6  # 限制测试步数

    while not data['gameOver'] and move_count < max_moves:
        print(f"\n回合 {move_count + 1}: {data['currentPlayer']}方")

        if data['currentPlayer'] == 'red':
            # 玩家移动（模拟）
            print("玩家移动...")
            # 这里可以模拟玩家移动，为了测试，我们让AI帮玩家移动
            response = requests.post(f"{BASE_URL}/api/ai_move", json={
                "player": data['currentPlayer'],
                "mode": data['gameMode']
            })
            ai_data = response.json()

            if 'gameOver' in ai_data and ai_data['gameOver']:
                print(f"玩家无路可走，游戏结束！获胜者: {ai_data['winner']}")
                break

            if ai_data['move']:
                print(f"玩家移动: ({ai_data['move']['fromRow']}, {ai_data['move']['fromCol']}) -> ({ai_data['move']['toRow']}, {ai_data['move']['toCol']})")

                # 执行移动
                response = requests.post(f"{BASE_URL}/api/move", json={
                    "fromRow": ai_data['move']['fromRow'],
                    "fromCol": ai_data['move']['fromCol'],
                    "toRow": ai_data['move']['toRow'],
                    "toCol": ai_data['move']['toCol'],
                    "mode": data['gameMode']
                })
                data = response.json()

                print(f"移动后: currentPlayer={data['currentPlayer']}, gameOver={data['gameOver']}")

                if data['gameOver']:
                    print(f"游戏结束！获胜者: {data['winner']}")
                    break
            else:
                print("玩家无法移动")
                break
        else:
            # AI移动
            print("AI移动...")
            response = requests.post(f"{BASE_URL}/api/ai_move", json={
                "player": data['currentPlayer'],
                "mode": data['gameMode']
            })
            ai_data = response.json()

            if 'gameOver' in ai_data and ai_data['gameOver']:
                print(f"AI无路可走，游戏结束！获胜者: {ai_data['winner']}")
                break

            if ai_data['move']:
                print(f"AI移动: ({ai_data['move']['fromRow']}, {ai_data['move']['fromCol']}) -> ({ai_data['move']['toRow']}, {ai_data['move']['toCol']})")

                # 执行移动
                response = requests.post(f"{BASE_URL}/api/move", json={
                    "fromRow": ai_data['move']['fromRow'],
                    "fromCol": ai_data['move']['fromCol'],
                    "toRow": ai_data['move']['toRow'],
                    "toCol": ai_data['move']['toCol'],
                    "mode": data['gameMode']
                })
                data = response.json()

                print(f"移动后: currentPlayer={data['currentPlayer']}, gameOver={data['gameOver']}")

                if data['gameOver']:
                    print(f"游戏结束！获胜者: {data['winner']}")
                    break
            else:
                print("AI无法移动")
                break

        move_count += 1
        time.sleep(0.5)  # 模拟延迟

    print(f"\n测试完成，共进行了 {move_count} 步")

if __name__ == "__main__":
    try:
        test_ai_vs_ai_mode()
        test_pve_mode()
        print("\n✅ 所有测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
