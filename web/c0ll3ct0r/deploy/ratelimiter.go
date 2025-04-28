package main

import (
	"net/http"
	"sync"
	"time"

	"github.com/labstack/echo/v4"
)

const rateLimit = 100

type RateLimiter struct {
	users map[int]*userLimit
	mu    sync.Mutex
}

type userLimit struct {
	count     int
	lastReset time.Time
	mu        *sync.Mutex
}

func (u *userLimit) Incr() {
	u.mu.Lock()
	defer u.mu.Unlock()
	u.count++
}

func (u *userLimit) Reset() {
	u.mu.Lock()
	defer u.mu.Unlock()
	u.count = 0
	u.lastReset = time.Now()
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		users: make(map[int]*userLimit, 4096),
	}
}

func (rl *RateLimiter) RateLimitMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		userID := c.Get("userId").(int)

		limit := rl.getUserLimit(userID)

		if time.Since(limit.lastReset) > 24*time.Hour {
			limit.Reset()
		}

		if limit.count >= rateLimit {
			return c.String(http.StatusTooManyRequests, "too many requests")
		}

		limit.Incr()
		return next(c)
	}
}

func (rl *RateLimiter) getUserLimit(userID int) *userLimit {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	limit, exists := rl.users[userID]
	if !exists {
		limit = &userLimit{
			count:     0,
			lastReset: time.Now(),
			mu:        &sync.Mutex{},
		}
		rl.users[userID] = limit
	}

	return limit
}
