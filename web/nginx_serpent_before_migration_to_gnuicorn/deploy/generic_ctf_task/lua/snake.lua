-- /usr/local/openresty/nginx/lua/snake.lua
local cjson = require "cjson"

-- Initialize game state if not already set
local function init_game_state()
  local state = ngx.shared.snake_game

  if not state:get("initialized") then
    -- Initial snake position (3 segments)
    local snake = { { x = 10, y = 10 }, { x = 9, y = 10 }, { x = 8, y = 10 } }
    -- Initial food position
    local food = { x = 15, y = 15 }

    state:set("snake", cjson.encode(snake))
    state:set("food", cjson.encode(food))
    state:set("direction", "right")
    state:set("score", 0)
    state:set("game_over", false)
    state:set("initialized", true)
  end
end

-- HTML/CSS/JS for the game UI
local html = [[
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NGINX Snake Game</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #222;
            font-family: Arial, sans-serif;
        }

        .game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        #game-board {
            width: 500px;
            height: 500px;
            background-color: #333;
            border: 2px solid #666;
            position: relative;
        }

        .snake-part {
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: #32CD32;
            border: 1px solid #228B22;
            box-sizing: border-box;
        }

        .snake-head {
            background-color: #7CFC00;
        }

        .food {
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: #FF4500;
            border: 1px solid #B22222;
            border-radius: 50%;
            box-sizing: border-box;
        }

        .controls {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }

        button {
            padding: 10px 15px;
            background-color: #444;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background-color: #555;
        }

        .score {
            color: white;
            font-size: 24px;
            margin-bottom: 10px;
        }

        .game-over {
            color: #FF4500;
            font-size: 30px;
            margin-bottom: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1 style="color: white;">NGINX Snake</h1>
        <div class="score">Score: <span id="score">0</span></div>
        <div class="game-over" id="game-over">Game Over!</div>
        <div id="game-board"></div>
        <div class="controls">
            <button id="restart">Restart Game</button>
        </div>
        <div style="color: #999; margin-top: 20px; text-align: center;">
            Use arrow keys to control the snake.<br>
            Powered by NGINX + Lua
        </div>
    </div>

    <script>
        const gameBoard = document.getElementById('game-board');
        const scoreElement = document.getElementById('score');
        const gameOverElement = document.getElementById('game-over');
        const gridSize = 20; // 20px per cell
        const gridWidth = 25; // 500px / 20px = 25 cells
        const gridHeight = 25;

        // Game state
        let snake = [];
        let food = {};
        let direction = "right";
        let score = 0;
        let gameOver = false;
        let gameLoopInterval = null;

        // Initialize the game
        function initGame() {
            fetchGameState();
        }

        // Fetch game state from server
        function fetchGameState() {
            fetch('/snake/state')
                .then(response => response.json())
                .then(data => {
                    snake = data.snake;
                    food = data.food;
                    direction = data.direction;
                    score = data.score;
                    gameOver = data.game_over;

                    updateUI();

                    if (!gameOver && !gameLoopInterval) {
                        startGameLoop();
                    }
                })
                .catch(error => console.error('Error fetching game state:', error));
        }

        // Start game loop
        function startGameLoop() {
            if (gameLoopInterval) clearInterval(gameLoopInterval);
            gameLoopInterval = setInterval(moveSnake, 150);
        }

        // Move snake in current direction
        function moveSnake() {
            if (gameOver) {
                clearInterval(gameLoopInterval);
                gameLoopInterval = null;
                return;
            }

            fetch(`/snake/move?direction=${direction}`)
                .then(response => response.json())
                .then(data => {
                    snake = data.snake;
                    food = data.food;
                    score = data.score;
                    gameOver = data.game_over;

                    updateUI();

                    if (gameOver) {
                        clearInterval(gameLoopInterval);
                        gameLoopInterval = null;
                    }
                })
                .catch(error => {
                    console.error('Error moving snake:', error);
                    clearInterval(gameLoopInterval);
                    gameLoopInterval = null;
                });
        }

        // Update UI based on game state
        function updateUI() {
            // Clear the board
            gameBoard.innerHTML = '';

            // Draw snake
            snake.forEach((part, index) => {
                const snakePart = document.createElement('div');
                snakePart.className = 'snake-part';
                if (index === 0) {
                    snakePart.classList.add('snake-head');
                }
                snakePart.style.left = `${part.x * gridSize}px`;
                snakePart.style.top = `${part.y * gridSize}px`;
                gameBoard.appendChild(snakePart);
            });

            // Draw food
            const foodElement = document.createElement('div');
            foodElement.className = 'food';
            foodElement.style.left = `${food.x * gridSize}px`;
            foodElement.style.top = `${food.y * gridSize}px`;
            gameBoard.appendChild(foodElement);

            // Update score
            scoreElement.textContent = score;

            // Show game over message if needed
            gameOverElement.style.display = gameOver ? 'block' : 'none';
        }

        // Keyboard controls
        document.addEventListener('keydown', (event) => {
            switch(event.key) {
                case 'ArrowUp':
                    if (direction !== 'down') direction = 'up';
                    break;
                case 'ArrowDown':
                    if (direction !== 'up') direction = 'down';
                    break;
                case 'ArrowLeft':
                    if (direction !== 'right') direction = 'left';
                    break;
                case 'ArrowRight':
                    if (direction !== 'left') direction = 'right';
                    break;
            }
        });

        // Restart game
        document.getElementById('restart').addEventListener('click', () => {
            fetch('/snake/restart')
                .then(() => {
                    if (gameLoopInterval) {
                        clearInterval(gameLoopInterval);
                        gameLoopInterval = null;
                    }
                    fetchGameState();
                })
                .catch(error => console.error('Error restarting game:', error));
        });

        // Start the game
        initGame();
    </script>
</body>
</html>
]]

-- Initialize game state and serve HTML
init_game_state()
ngx.say(html)
