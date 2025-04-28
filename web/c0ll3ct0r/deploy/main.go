package main

import (
	"context"
	"errors"
	"fmt"
	"github.com/go-redis/redis/v8"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"html/template"
	"log"
	"net/http"
	"os"
)

type Service struct {
	db     *pgxpool.Pool
	redis  *redis.Client
	server *echo.Echo
}

func NewService(db *pgxpool.Pool, redis *redis.Client, server *echo.Echo) *Service {
	return &Service{
		db:     db,
		redis:  redis,
		server: server,
	}
}

func (s *Service) ListenAndServe() {
	s.server.Use(middleware.Logger())
	s.server.Use(middleware.Recover())

	rl := NewRateLimiter()

	// POST ручки
	s.server.POST("/collect", s.PostCollect, s.AuthMiddleware, rl.RateLimitMiddleware)
	s.server.POST("/login", s.PostLogin)
	s.server.POST("/logout", s.PostLogout, s.AuthMiddleware)
	s.server.POST("/signup", s.PostSignup)

	// GET ручки
	s.server.GET("/", s.GetIndex)
	s.server.GET("/collect", s.GetCollect, s.AuthMiddleware)
	s.server.Renderer = &Template{
		templates: template.Must(template.ParseGlob("templates/*.html")),
	}
	s.server.Static("/static", "static")

	if err := s.server.Start(":8080"); err != nil && errors.Is(err, http.ErrServerClosed) {
		log.Fatalf("listen: %s\n", err)
	}
}

func main() {
	postgresHost, redisHost := "localhost", "localhost"
	if os.Getenv("ENVIRONMENT") == "production" {
		postgresHost = "postgres"
		redisHost = "redis"
	}

	db, err := pgxpool.Connect(context.Background(), fmt.Sprintf("postgres://postgres:postgres@%s:5432/postgres", postgresHost))
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
	}
	defer db.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr:     redisHost + ":6379",
		Username: "redis",
		Password: "redis",
	})

	server := echo.New()

	service := NewService(db, redisClient, server)
	service.ListenAndServe()
}
