-- /usr/local/openresty/nginx/lua/secret_snake.lua
local cjson = require "cjson"

-- Initialize game state if not already set
local function init_game_state()
  local state = ngx.shared.snake_game

  if not state:get("initialized") then
    -- Initial snake position (3 segments)
    local snake = { { x = 10, y = 10 }, { x = 9, y = 10 }, { x = 8, y = 10 } }
    -- Initial food position
    local food = { x = 15, y = 15 }
    -- Initial special food (secret)
    local special_food = { x = 5, y = 5 }

    state:set("snake", cjson.encode(snake))
    state:set("food", cjson.encode(food))
    state:set("special_food", cjson.encode(special_food))
    state:set("direction", "right")
    state:set("score", 0)
    state:set("special_food_count", 0)
    state:set("game_over", false)
    state:set("flag_unlocked", false)
    state:set("initialized", true)
  end
end

-- HTML/CSS/JS for the game UI with special modifications
local html = [[
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NGINX Snake Game - CTF Challenge</title>
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

        .special-food {
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: #FFD700;  /* Gold color */
            border: 1px solid #DAA520;
            border-radius: 50%;
            box-sizing: border-box;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
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

        .flag-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            flex-direction: column;
            display: none;
        }

        .flag-message {
            background-color: #32CD32;
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 24px;
            max-width: 80%;
        }

        .flag-hint {
            background-color: #007BFF;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 16px;
            max-width: 80%;
            display: none;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1 style="color: white;">NGINX Snake - Secret Challenge</h1>
        <div class="score">Score: <span id="score">0</span></div>
        <div class="game-over" id="game-over">Game Over!</div>
        <div id="game-board"></div>
        <div class="controls">
            <button id="restart">Restart Game</button>
        </div>
        <div style="color: #999; margin-top: 20px; text-align: center;">
            Use arrow keys to control the snake.<br>
            <span style="color: #FFD700;">Golden food items are special!</span><br>
            Powered by NGINX + Lua
        </div>
        <div class="flag-hint" id="flag-hint" style="display:none;"></div>
    </div>

    <div class="flag-container" id="flag-container">
        <div class="flag-message" id="flag-message">
            <p>You found a piece of the flag!</p>
            <p id="flag-value"></p>
        </div>
        <button style="margin-top: 20px;" onclick="document.getElementById('flag-container').style.display='none';">Close</button>
    </div>

    <script>
        const gameBoard = document.getElementById('game-board');
        const scoreElement = document.getElementById('score');
        const gameOverElement = document.getElementById('game-over');
        const flagContainer = document.getElementById('flag-container');
        const flagValue = document.getElementById('flag-value');
        const flagHint = document.getElementById('flag-hint');
        const gridSize = 20; // 20px per cell
        const gridWidth = 25; // 500px / 20px = 25 cells
        const gridHeight = 25;

        // Game state
        let snake = [];
        let food = {};
        let specialFood = null;
        let direction = "right";
        let score = 0;
        let gameOver = false;
        let gameLoopInterval = null;
        let flagPieces = [];
        let specialFoodCount = 0;

        // Initialize the game
        function initGame() {
            fetchGameState();
        }

        // Fetch game state from server
        function fetchGameState() {
            fetch('/snake/state')
                .then(response => {
                    // Store headers for later inspection
                    const headers = {};
                    response.headers.forEach((value, name) => {
                        headers[name.toLowerCase()] = value;
                    });

                    // Check for flag pieces in headers
                    if (headers['x-flag-part-2']) {
                        const flagPart = headers['x-flag-part-2'];
                        if (!flagPieces.includes(flagPart)) {
                            flagPieces.push(flagPart);
                            showFlagPiece(flagPart);
                        }
                    }

                    return response.json();
                })
                .then(data => {
                    snake = data.snake;
                    food = data.food;
                    specialFood = data.special_food;
                    direction = data.direction;
                    score = data.score;
                    gameOver = data.game_over;
                    specialFoodCount = data.special_food_count || 0;

                    // Check for flag hints
                    if (data.flag_hint) {
                        flagHint.textContent = data.flag_hint;
                        flagHint.style.display = 'block';
                    }

                    // Check for flag pieces
                    if (data.flag_part && !flagPieces.includes(data.flag_part)) {
                        flagPieces.push(data.flag_part);
                        showFlagPiece(data.flag_part);
                    }

                    updateUI();

                    if (!gameOver && !gameLoopInterval) {
                        startGameLoop();
                    }
                })
                .catch(error => console.error('Error fetching game state:', error));
        }

        function showFlagPiece(piece) {
            flagValue.textContent = `Flag piece: ${piece}`;
            flagContainer.style.display = 'flex';
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
                .then(response => {
                    // Store headers for later inspection
                    const headers = {};
                    response.headers.forEach((value, name) => {
                        headers[name.toLowerCase()] = value;
                    });

                    // Check for flag pieces in headers
                    if (headers['x-flag-part-2']) {
                        const flagPart = headers['x-flag-part-2'];
                        if (!flagPieces.includes(flagPart)) {
                            flagPieces.push(flagPart);
                            showFlagPiece(flagPart);
                        }
                    }

                    return response.json();
                })
                .then(data => {
                    snake = data.snake;
                    food = data.food;
                    specialFood = data.special_food;
                    score = data.score;
                    gameOver = data.game_over;
                    specialFoodCount = data.special_food_count || 0;

                    // Check for flag hints
                    if (data.flag_hint) {
                        flagHint.textContent = data.flag_hint;
                        flagHint.style.display = 'block';
                    }

                    // Check for flag pieces
                    if (data.flag_part && !flagPieces.includes(data.flag_part)) {
                        flagPieces.push(data.flag_part);
                        showFlagPiece(data.flag_part);
                    }

                    updateUI();

                    if (gameOver) {
                        clearInterval(gameLoopInterval);
                        gameLoopInterval = null;

                        // Check for completed special food collection
                        if (specialFoodCount >= 3) {
                            flagHint.textContent = "You've collected all the special food! Now try checking the /flag-piece endpoint with different HTTP methods...";
                            flagHint.style.display = 'block';
                        }
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

            // Draw special food if available
            if (specialFood) {
                const specialFoodElement = document.createElement('div');
                specialFoodElement.className = 'special-food';
                specialFoodElement.style.left = `${specialFood.x * gridSize}px`;
                specialFoodElement.style.top = `${specialFood.y * gridSize}px`;
                gameBoard.appendChild(specialFoodElement);
            }

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
                // Secret key combination to reveal a hint
                case 'h':
                    if (event.ctrlKey && event.shiftKey) {
                        flagHint.textContent = "Try removing the Host header or using a non-matching hostname! Also try different HTTP methods on /flag-piece";
                        flagHint.style.display = 'block';
                    }
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

        // Check all HTTP methods on flag-piece endpoint
        function checkAllHttpMethods() {
            // Just a console hint for advanced players
            console.log("Try sending OPTIONS and HEAD requests to the /flag-piece endpoint!");
        }

        setTimeout(checkAllHttpMethods, 10000);
    </script>
</body>
</html>
]]

-- Initialize game state and serve HTML
init_game_state()
ngx.say(html)
