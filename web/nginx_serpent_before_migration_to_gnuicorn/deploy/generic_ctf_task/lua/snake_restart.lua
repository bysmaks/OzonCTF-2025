-- /usr/local/openresty/nginx/lua/snake_restart.lua
local cjson = require "cjson"
local state = ngx.shared.snake_game

-- Reset game to initial state
local snake = { { x = 10, y = 10 }, { x = 9, y = 10 }, { x = 8, y = 10 } }
local food = { x = 15, y = 15 }
local special_food = { x = 5, y = 5 }

-- Generate random food position
local valid_food = false
while not valid_food do
  local new_x = math.random(0, 24)
  local new_y = math.random(0, 24)

  valid_food = true
  for i = 1, #snake do
    if snake[i].x == new_x and snake[i].y == new_y then
      valid_food = false
      break
    end
  end

  if valid_food then
    food = { x = new_x, y = new_y }
  end
end

-- Generate random special food position
valid_food = false
while not valid_food do
  local new_x = math.random(0, 24)
  local new_y = math.random(0, 24)

  valid_food = true
  -- Check not on snake
  for i = 1, #snake do
    if snake[i].x == new_x and snake[i].y == new_y then
      valid_food = false
      break
    end
  end

  -- Check not on regular food
  if food.x == new_x and food.y == new_y then
    valid_food = false
  end

  if valid_food then
    special_food = { x = new_x, y = new_y }
  end
end

-- Set initial state
state:set("snake", cjson.encode(snake))
state:set("food", cjson.encode(food))
state:set("special_food", cjson.encode(special_food))
state:set("direction", "right")
state:set("score", 0)
state:set("special_food_count", 0)
state:set("game_over", false)
state:set("initialized", true)

-- Return success
ngx.header["Content-Type"] = "application/json"
ngx.say('{"status":"success"}')
