-- /usr/local/openresty/nginx/lua/snake_move.lua
local cjson = require "cjson"
local state = ngx.shared.snake_game

-- Get current direction and requested direction
local current_direction = state:get("direction")
local new_direction = ngx.req.get_uri_args().direction

-- Check if the new direction is valid (not 180 degrees from current)
if new_direction then
  if (new_direction == "up" and current_direction ~= "down") or
      (new_direction == "down" and current_direction ~= "up") or
      (new_direction == "left" and current_direction ~= "right") or
      (new_direction == "right" and current_direction ~= "left") then
    state:set("direction", new_direction)
    current_direction = new_direction
  end
end

-- Get current game state
local snake = cjson.decode(state:get("snake"))
local food = cjson.decode(state:get("food"))
local special_food = state:get("special_food") and cjson.decode(state:get("special_food")) or nil
local score = state:get("score")
local game_over = state:get("game_over")
local special_food_count = state:get("special_food_count") or 0

-- Don't update if game is over
if game_over then
  ngx.header["Content-Type"] = "application/json"
  ngx.say(cjson.encode({
    snake = snake,
    food = food,
    special_food = special_food,
    direction = current_direction,
    score = score,
    game_over = game_over,
    special_food_count = special_food_count
  }))
  return
end

-- Calculate new head position
local head = { x = snake[1].x, y = snake[1].y }

if current_direction == "up" then
  head.y = head.y - 1
elseif current_direction == "down" then
  head.y = head.y + 1
elseif current_direction == "left" then
  head.x = head.x - 1
elseif current_direction == "right" then
  head.x = head.x + 1
end

-- Check for wall collision (25x25 grid)
if head.x < 0 or head.x >= 25 or head.y < 0 or head.y >= 25 then
  state:set("game_over", true)
  game_over = true
else
  -- Check for self collision
  for i = 1, #snake do
    if head.x == snake[i].x and head.y == snake[i].y then
      state:set("game_over", true)
      game_over = true
      break
    end
  end
end

-- If no collision, update snake position
if not game_over then
  -- Add new head
  table.insert(snake, 1, head)

  -- Check if snake ate food
  if head.x == food.x and head.y == food.y then
    -- Increase score
    score = score + 1
    state:set("score", score)

    -- Generate new food position
    local valid_food = false
    while not valid_food do
      -- Random position on 25x25 grid
      local new_x = math.random(0, 24)
      local new_y = math.random(0, 24)

      -- Make sure food isn't on snake or special food
      valid_food = true
      for i = 1, #snake do
        if snake[i].x == new_x and snake[i].y == new_y then
          valid_food = false
          break
        end
      end

      -- Check against special food if it exists
      if valid_food and special_food and new_x == special_food.x and new_y == special_food.y then
        valid_food = false
      end

      if valid_food then
        food = { x = new_x, y = new_y }
      end
    end

    state:set("food", cjson.encode(food))
    -- Check if snake ate special food
  elseif special_food and head.x == special_food.x and head.y == special_food.y then
    -- Increase score (special food worth more points)
    score = score + 50
    state:set("score", score)

    -- Increment special food counter
    special_food_count = special_food_count + 1
    state:set("special_food_count", special_food_count)

    -- Generate new special food position if we haven't collected 3 yet
    if special_food_count < 3 then
      local valid_food = false
      while not valid_food do
        -- Random position on 25x25 grid
        local new_x = math.random(0, 24)
        local new_y = math.random(0, 24)

        -- Make sure special food isn't on snake or regular food
        valid_food = true
        for i = 1, #snake do
          if snake[i].x == new_x and snake[i].y == new_y then
            valid_food = false
            break
          end
        end

        -- Check against regular food
        if valid_food and food.x == new_x and food.y == new_y then
          valid_food = false
        end

        if valid_food then
          special_food = { x = new_x, y = new_y }
        end
      end

      state:set("special_food", cjson.encode(special_food))
    else
      -- We've collected all 3, remove special food
      special_food = nil
      state:set("special_food", nil)
    end
  else
    -- Remove tail if no food eaten
    table.remove(snake)
  end

  -- Update snake in state
  state:set("snake", cjson.encode(snake))
end

-- Flag hint based on special food collection
local flag_hint = nil
if special_food_count >= 3 then
  flag_hint = "You've collected all the special food! Now try HEAD and OPTIONS requests to /flag-piece"
elseif special_food_count > 0 then
  flag_hint = "Find more golden food! You've found " .. special_food_count .. " of 3"
end

-- Return updated state
ngx.header["Content-Type"] = "application/json"
ngx.say(cjson.encode({
  snake = snake,
  food = food,
  special_food = special_food,
  direction = current_direction,
  score = score,
  game_over = game_over,
  special_food_count = special_food_count,
  flag_hint = flag_hint,
  flag_part = special_food_count >= 3 and "default_server_first_" or nil
}))
