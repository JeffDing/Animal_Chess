// 游戏状态
let gameState = {
    board: [],
    currentPlayer: 'red',
    gameOver: false,
    winner: null,
    selectedPiece: null,
    validMoves: [],
    gameMode: 'pvp', // 'pvp', 'pve', 'aivai'
    aiDifficulty: 'amateur' // 'easy', 'medium', 'hard', 'expert'
};

// 棋子图标映射
const pieceIcons = {
    '象': '🐘',
    '狮': '🦁',
    '虎': '🐯',
    '豹': '🐆',
    '狼': '🐺',
    '狗': '🐕',
    '猫': '🐱',
    '鼠': '🐀'
};

// 河流位置
const riverPositions = [
    [3, 1], [3, 2], [4, 1], [4, 2], [5, 1], [5, 2],
    [3, 4], [3, 5], [4, 4], [4, 5], [5, 4], [5, 5]
];

// 兽穴位置
const denPositions = {
    'red': [0, 3],
    'blue': [8, 3]
};

// 陷阱位置
const trapPositions = {
    'red': [[0, 2], [0, 4], [1, 3]],
    'blue': [[8, 2], [8, 4], [7, 3]]
};

// 初始化游戏
function initGame() {
    fetch('/api/init', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        gameState = data;
        renderBoard();
        updateStatus();
    });
}

// 切换游戏模式
function switchMode(mode) {
    gameState.gameMode = mode;
    
    // 更新按钮状态
    document.querySelectorAll('.controls .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    if (mode === 'pvp') {
        document.getElementById('btnPvP').classList.add('active');
    } else if (mode === 'pve') {
        document.getElementById('btnPvE').classList.add('active');
    } else if (mode === 'aivai') {
        document.getElementById('btnAIvAI').classList.add('active');
    }
    
    // 更新模式显示
    const modeNames = {
        'pvp': '人人对战',
        'pve': '人机对战',
        'aivai': 'AI对战'
    };
    document.getElementById('modeInfo').textContent = '当前模式：' + modeNames[mode];

      // 显示或隐藏难度选择器
      const difficultyControls = document.getElementById('difficultyControls');
      if (mode === 'pve' || mode === 'aivai') {
          difficultyControls.style.display = 'block';
      } else {
          difficultyControls.style.display = 'none';
      }
    
    // 开始新游戏
    startNewGame();
}

// 开始新游戏
function startNewGame() {
    fetch('/api/new_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode: gameState.gameMode,
              difficulty: gameState.aiDifficulty })
    })
    .then(response => response.json())
    .then(data => {
        gameState = data;
        gameState.gameMode = gameState.gameMode || 'pvp';
        gameState.selectedPiece = null;
        gameState.validMoves = [];
        renderBoard();
        updateStatus();
        
        // 如果是AI对战模式，自动开始
        if (gameState.gameMode === 'aivai') {
            setTimeout(makeAIMove, 500);
        }
    });
}

// 渲染棋盘
function renderBoard() {
    const boardElement = document.getElementById('gameBoard');
    boardElement.innerHTML = '';
    
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 7; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            
            // 设置特殊格子样式
            if (isRiver(row, col)) {
                cell.classList.add('river');
            } else if (isDen(row, col, 'red')) {
                cell.classList.add('den-red');
            } else if (isDen(row, col, 'blue')) {
                cell.classList.add('den-blue');
            } else if (isTrap(row, col)) {
                cell.classList.add('trap');
            }
            
            // 添加棋子
            const piece = gameState.board[row][col];
            if (piece) {
                const pieceElement = document.createElement('div');
                pieceElement.className = `piece ${piece.player}`;
                pieceElement.innerHTML = `
                    ${pieceIcons[piece.name]}
                    <span class="rank">${piece.rank}</span>
                `;
                cell.appendChild(pieceElement);
            }
            
            // 标记选中的棋子
            if (gameState.selectedPiece && 
                gameState.selectedPiece.row === row && 
                gameState.selectedPiece.col === col) {
                cell.classList.add('selected');
            }
            
            // 标记有效移动位置
            if (gameState.validMoves.some(move => move.toRow === row && move.toCol === col)) {
                cell.classList.add('valid-move');
            }
            
            cell.addEventListener('click', () => handleCellClick(row, col));
            boardElement.appendChild(cell);
        }
    }
}

// 判断是否是河流
function isRiver(row, col) {
    return riverPositions.some(pos => pos[0] === row && pos[1] === col);
}

// 判断是否是兽穴
function isDen(row, col, player) {
    const denPos = denPositions[player];
    return denPos[0] === row && denPos[1] === col;
}

// 判断是否是陷阱
function isTrap(row, col) {
    return [...trapPositions.red, ...trapPositions.blue].some(pos => pos[0] === row && pos[1] === col);
}

// 处理格子点击
function handleCellClick(row, col) {
    if (gameState.gameOver) {
        return;
    }
    
    // 如果是AI回合，不允许玩家操作
    if (gameState.gameMode === 'pve' && gameState.currentPlayer === 'blue') {
        return;
    }
    
    // 如果是AI对战模式，不允许玩家操作
    if (gameState.gameMode === 'aivai') {
        return;
    }
    
    const piece = gameState.board[row][col];
    
    // 如果点击的是有效移动位置
    if (gameState.selectedPiece && 
        gameState.validMoves.some(move => move.toRow === row && move.toCol === col)) {
        makeMove(gameState.selectedPiece.row, gameState.selectedPiece.col, row, col);
        return;
    }
    
    // 如果点击的是当前玩家的棋子
    if (piece && piece.player === gameState.currentPlayer) {
        gameState.selectedPiece = { row, col };
        fetch('/api/valid_moves', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fromRow: row,
                fromCol: col,
                player: gameState.currentPlayer
            })
        })
        .then(response => response.json())
        .then(data => {
            gameState.validMoves = data.moves;
            renderBoard();
        });
    } else {
        // 取消选择
        gameState.selectedPiece = null;
        gameState.validMoves = [];
        renderBoard();
    }
}

// 执行移动
function makeMove(fromRow, fromCol, toRow, toCol) {
    fetch('/api/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            fromRow: fromRow,
            fromCol: fromCol,
            toRow: toRow,
            toCol: toCol,
            mode: gameState.gameMode,
              difficulty: gameState.aiDifficulty
        })
    })
    .then(response => response.json())
    .then(data => {
        gameState = data;
        gameState.selectedPiece = null;
        gameState.validMoves = [];
        renderBoard();
        updateStatus();

        // 检查游戏是否结束
        if (gameState.gameOver) {
            showWinner();
            return;
        }

        // 如果是人机对战且轮到蓝方（AI）
        if (gameState.gameMode === 'pve' && gameState.currentPlayer === 'blue') {
            setTimeout(makeAIMove, 500);
        }

        // 如果是AI对战模式
        if (gameState.gameMode === 'aivai') {
            setTimeout(makeAIMove, 500);
        }
    });
}

// AI移动
function makeAIMove() {
    if (gameState.gameOver) {
        return;
    }

    fetch('/api/ai_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            player: gameState.currentPlayer,
            mode: gameState.gameMode,
              difficulty: gameState.aiDifficulty
        })
    })
    .then(response => response.json())
    .then(data => {
        // 检查游戏是否结束
        if (data.gameOver) {
            gameState = data;
            gameState.selectedPiece = null;
            gameState.validMoves = [];
            renderBoard();
            updateStatus();
            showWinner();
            return;
        }

        if (data.move) {
            makeMove(data.move.fromRow, data.move.fromCol, data.move.toRow, data.move.toCol);
        } else {
            // AI无路可走，游戏结束
            console.log('AI无路可走，游戏结束');
        }
    })
    .catch(error => {
        console.error('AI移动失败:', error);
    });
}

// 更新状态显示
function updateStatus() {
    const statusElement = document.getElementById('gameStatus');
    
    if (gameState.gameOver) {
        const winnerText = gameState.winner === 'red' ? '红方' : '蓝方';
        statusElement.textContent = `游戏结束！${winnerText}获胜！`;
        statusElement.style.color = gameState.winner === 'red' ? '#e74c3c' : '#16a085';
    } else {
        const playerText = gameState.currentPlayer === 'red' ? '红方' : '蓝方';
        statusElement.textContent = `${playerText}回合`;
        statusElement.style.color = gameState.currentPlayer === 'red' ? '#e74c3c' : '#16a085';
    }
}

// 显示获胜者
function showWinner() {
    const overlay = document.createElement('div');
    overlay.className = 'winner-overlay';
    
    const winnerText = gameState.winner === 'red' ? '红方' : '蓝方';
    const winnerClass = gameState.winner;
    
    overlay.innerHTML = `
        <div class="winner-message">
            <h2>🎉 游戏结束 🎉</h2>
            <div class="winner-name ${winnerClass}">${winnerText}获胜！</div>
            <button onclick="closeWinnerOverlay()">关闭</button>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

// 关闭获胜弹窗
function closeWinnerOverlay() {
    const overlay = document.querySelector('.winner-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// 页面加载时初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    initGame();
    // 默认选中人人对战模式
    document.getElementById('btnPvP').classList.add('active');
    
    // 确保模式信息正确显示
    document.getElementById('modeInfo').textContent = '当前模式：人人对战';
});

  // 切换AI难度
  function changeDifficulty(difficulty) {
      gameState.aiDifficulty = difficulty;

      // 更新难度描述
      const descriptions = {
          'beginner': '入门级别：AI基本不思考，随机性很强，适合完全新手',
          'easy': '简单级别：AI有少量前瞻，会犯一些错误，适合新手',
          'amateur': '业余级别：AI有基本策略，适合有一定经验的玩家',
          'professional': '专业级别：AI策略性强，会深度思考，适合高手',
          'master': '大师级别：AI极难战胜，会深度思考和战术分析，追求极致'
      };

      document.getElementById('difficultyDescription').textContent = descriptions[difficulty];
  }
