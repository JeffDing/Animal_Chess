from flask import Flask, render_template, jsonify, request
from game_logic import DoushouqiGame
import random

app = Flask(__name__)

# 全局游戏实例
game = DoushouqiGame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_game():
    """初始化游戏"""
    global game
    game = DoushouqiGame()
    return jsonify({
        'board': game.get_board_state(),
        'currentPlayer': game.current_player,
        'gameOver': game.game_over,
        'winner': game.winner,
        'gameMode': 'pvp'
    })

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """开始新游戏"""
    global game
    data = request.json
    game_mode = data.get('mode', 'pvp')
    game = DoushouqiGame()
    return jsonify({
        'board': game.get_board_state(),
        'currentPlayer': game.current_player,
        'gameOver': game.game_over,
        'winner': game.winner,
        'gameMode': game_mode
    })

@app.route('/api/valid_moves', methods=['POST'])
def get_valid_moves():
    """获取有效移动"""
    data = request.json
    from_row = data['fromRow']
    from_col = data['fromCol']
    player = data['player']
    
    moves = []
    for to_row in range(9):
        for to_col in range(7):
            if game.is_valid_move(from_row, from_col, to_row, to_col, player):
                moves.append({
                    'fromRow': from_row,
                    'fromCol': from_col,
                    'toRow': to_row,
                    'toCol': to_col
                })
    
    return jsonify({'moves': moves})

@app.route('/api/move', methods=['POST'])
def make_move():
    """执行移动"""
    data = request.json
    from_row = data['fromRow']
    from_col = data['fromCol']
    to_row = data['toRow']
    to_col = data['toCol']
    
    success = game.make_move(from_row, from_col, to_row, to_col)
    
    # 检查是否无路可走
    if not game.game_over:
        opponent = 'blue' if game.current_player == 'red' else 'red'
        opponent_moves = game.get_valid_moves(opponent)
        if not opponent_moves:
            # 无路可走，当前玩家获胜
            game.game_over = True
            game.winner = game.current_player
    
    return jsonify({
        'board': game.get_board_state(),
        'currentPlayer': game.current_player,
        'gameOver': game.game_over,
        'winner': game.winner,
        'gameMode': request.json.get('mode', 'pvp')
    })

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """AI移动"""
    player = request.json.get('player', 'blue')

    # 获取所有有效移动
    valid_moves = game.get_valid_moves(player)

    if not valid_moves:
        # AI无路可走，对方获胜
        opponent = 'blue' if player == 'red' else 'red'
        game.game_over = True
        game.winner = opponent
        return jsonify({
            'move': None,
            'board': game.get_board_state(),
            'currentPlayer': player,
            'gameOver': True,
            'winner': opponent,
            'gameMode': request.json.get('mode', 'pvp')
        })

    # 简单的AI策略：评估每个移动的价值
    best_move = None
    best_score = -float('inf')

    for move in valid_moves:
        score = evaluate_move(move, player)
        if score > best_score:
            best_score = score
            best_move = move

    # 如果有多个相同分数的移动，随机选择一个
    best_moves = [move for move in valid_moves if evaluate_move(move, player) == best_score]

    # 确保best_moves不为空
    if best_moves:
        best_move = random.choice(best_moves)
    elif best_move is None and valid_moves:
        # 如果best_move为空但valid_moves不为空，随机选择一个
        best_move = random.choice(valid_moves)

    # 如果仍然没有找到最佳移动，返回None
    if best_move is None:
        # AI无路可走，对方获胜
        opponent = 'blue' if player == 'red' else 'red'
        game.game_over = True
        game.winner = opponent
        return jsonify({
            'move': None,
            'board': game.get_board_state(),
            'currentPlayer': player,
            'gameOver': True,
            'winner': opponent,
            'gameMode': request.json.get('mode', 'pvp')
        })

    return jsonify({
        'move': {
            'fromRow': best_move[0],
            'fromCol': best_move[1],
            'toRow': best_move[2],
            'toCol': best_move[3]
        }
    })

def evaluate_move(move, player):
    """评估移动的价值"""
    from_row, from_col, to_row, to_col = move
    
    # 模拟移动
    temp_game = game.clone()
    temp_game.make_move(from_row, from_col, to_row, to_col)
    
    score = 0
    
    # 1. 如果能吃掉对方棋子，加分
    target_piece = game.board[to_row][to_col]
    if target_piece and target_piece.player != player:
        score += target_piece.rank * 15
    
    # 2. 如果能进入对方兽穴，加大量分
    opponent = 'blue' if player == 'red' else 'red'
    if (to_row, to_col) == temp_game.den_positions[opponent]:
        score += 2000
    
    # 3. 如果移动后能保护自己的棋子，加分
    piece = game.board[from_row][from_col]
    if piece:
        # 检查目标位置是否在对方陷阱中
        if temp_game.is_trap(to_row, to_col, player):
            score -= piece.rank * 25
        
        # 检查是否靠近对方兽穴
        den_pos = temp_game.den_positions[opponent]
        distance_to_den = abs(to_row - den_pos[0]) + abs(to_col - den_pos[1])
        score += (12 - distance_to_den) * 3
    
    # 4. 优先移动高等级棋子
    if piece:
        score += piece.rank * 2
    
    # 5. 优先向对方兽穴方向移动
    if player == 'red':
        score += (to_row * 3)
    else:
        score += ((8 - to_row) * 3)
    
    # 6. 如果移动能让自己棋子更安全，加分
    for row in range(9):
        for col in range(7):
            p = temp_game.board[row][col]
            if p and p.player == player:
                # 检查这个棋子是否危险
                for other_row in range(9):
                    for other_col in range(7):
                        other = temp_game.board[other_row][other_col]
                        if other and other.player != player:
                            if temp_game.is_valid_move(other_row, other_col, row, col, other.player):
                                if other.rank > p.rank:
                                    score -= p.rank * 2
    
    # 7. 保护重要棋子（象、狮、虎）
    if piece and piece.rank >= 6:
        # 检查移动后是否安全
        danger_count = 0
        for other_row in range(9):
            for other_col in range(7):
                other = temp_game.board[other_row][other_col]
                if other and other.player != player:
                    if temp_game.is_valid_move(other_row, other_col, to_row, to_col, other.player):
                        if other.rank >= piece.rank:
                            danger_count += 1
        if danger_count == 0:
            score += piece.rank * 5
        else:
            score -= piece.rank * danger_count * 3
    
    # 8. 优先进入对方陷阱区域
    trap_zone = temp_game.trap_positions[opponent]
    for trap_pos in trap_zone:
        if abs(to_row - trap_pos[0]) + abs(to_col - trap_pos[1]) <= 2:
            score += 10
    
    # 9. 避免自己的棋子被吃
    original_piece = game.board[from_row][from_col]
    if original_piece:
        # 检查原位置是否危险
        danger_before = 0
        for other_row in range(9):
            for other_col in range(7):
                other = game.board[other_row][other_col]
                if other and other.player != player:
                    if game.is_valid_move(other_row, other_col, from_row, from_col, other.player):
                        if other.rank >= original_piece.rank:
                            danger_before += 1
        
        # 检查新位置是否危险
        danger_after = 0
        for other_row in range(9):
            for other_col in range(7):
                other = temp_game.board[other_row][other_col]
                if other and other.player != player:
                    if temp_game.is_valid_move(other_row, other_col, to_row, to_col, other.player):
                        if other.rank >= original_piece.rank:
                            danger_after += 1
        
        if danger_before > danger_after:
            score += (danger_before - danger_after) * original_piece.rank * 2
    
    # 10. 随机因素，让AI更有变化
    score += random.uniform(0, 10)
    
    return score

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
