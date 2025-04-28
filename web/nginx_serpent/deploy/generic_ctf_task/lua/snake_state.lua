-- /usr/local/openresty/nginx/lua/snake_state.lua
local cjson = require "cjson"

local state = ngx.shared.snake_game

-- Make sure state is initialized
if not state:get("initialized") then
  -- Initial snake position (3 segments)
  local snake = { { x = 10, y = 10 }, { x = 9, y = 10 }, { x = 8, y = 10 } }
  -- Initial food position
  local food = { x = 15, y = 15 }
  -- Initial special food (for secret game)
  local special_food = { x = 5, y = 5 }

  state:set("snake", cjson.encode(snake))
  state:set("food", cjson.encode(food))
  state:set("special_food", cjson.encode(special_food))
  state:set("direction", "right")
  state:set("score", 0)
  state:set("special_food_count", 0)
  state:set("game_over", false)
  state:set("initialized", true)
end

-- Return current game state as JSON
local response = {
  snake = cjson.decode(state:get("snake") or '[]'),
  food = cjson.decode(state:get("food") or '{"x":10,"y":10}'),
  special_food = state:get("special_food") and cjson.decode(state:get("special_food")) or nil,
  direction = state:get("direction") or "right",
  score = state:get("score") or 0,
  game_over = state:get("game_over") or false,
  special_food_count = state:get("special_food_count") or 0
}

-- Add flag part for special food collection
if state:get("special_food_count") and state:get("special_food_count") >= 3 then
  response.flag_part = "default_server_first_"
  response.flag_hint = "You've collected all special food! Now try HEAD and OPTIONS requests to /flag-piece"
elseif state:get("special_food_count") and state:get("special_food_count") > 0 then
  response.flag_hint = "Find more golden food! You've found " .. state:get("special_food_count") .. " of 3"
end

-- Check request headers for extra hints
local host = ngx.var.host or ""
if host == "" or host == "localhost" or host == "127.0.0.1" or not ngx.re.match(host, "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$") then
  -- Extra hint for people who found the right approach
  ngx.header["X-Next-Step"] = "Try HEAD and OPTIONS methods on /flag-piece"
end

ngx.header["Content-Type"] = "application/json"
ngx.say(cjson.encode(response))
