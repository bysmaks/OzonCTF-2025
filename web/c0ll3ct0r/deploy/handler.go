package main

import (
	"errors"
	"fmt"
	"github.com/go-redis/redis/v8"
	"golang.org/x/crypto/bcrypt"
	"log"
	"net/http"
	"net/url"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/andelf/go-curl"
	"github.com/golang-jwt/jwt"
	"github.com/labstack/echo/v4"
)

// PostCollectRequest — структура-заглушка для запроса /collect
type PostCollectRequest struct {
	URL string `json:"url"` // Добавил поле URL, чтобы вы могли использовать его
}

type User struct {
	UserId       int    `json:"id"`
	Login        string `json:"login"`
	PasswordHash string `json:"-"`
}

type Claims struct {
	Id    int    `json:"id"`
	Login string `json:"login"`
	jwt.StandardClaims
}

func (s *Service) GetIndex(c echo.Context) error {
	return c.Render(http.StatusOK, "index.html", nil)
}

func UrlCounterKey(userId int, login string) string {
	return fmt.Sprintf("user:%d_%s:url_counter", userId, login)
}

func (s *Service) GetCollect(c echo.Context) error {
	userId, ok := c.Get("userId").(int)
	if !ok {
		return c.String(http.StatusUnauthorized, "User not authenticated")
	}

	login, ok := c.Get("login").(string)
	if !ok {
		return c.String(http.StatusUnauthorized, "User not authenticated")
	}

	urlsCount, err := s.redis.Get(c.Request().Context(), UrlCounterKey(userId, login)).Result()
	if err != nil && !errors.Is(err, redis.Nil) {
		log.Println(err)
		return c.String(http.StatusUnauthorized, "User not authenticated")
	}

	urlsCountInt := 0
	if urlsCount != "" {
		urlsCountIntParsed, err := strconv.Atoi(urlsCount)
		if err == nil {
			urlsCountInt = urlsCountIntParsed
		}
	}

	flag := "????????????????????"
	if urlsCountInt > 1000000000 {
		flag = FLAG
	}

	return c.Render(http.StatusOK, "collect.html", map[string]interface{}{"flag": flag, "urlCount": urlsCountInt})
}

func (s *Service) PostCollect(c echo.Context) error {
	var req PostCollectRequest
	if err := c.Bind(&req); err != nil {
		return c.String(http.StatusBadRequest, "Invalid request")
	}

	if len(req.URL) > 255 || len(req.URL) < 4 {
		return c.String(http.StatusBadRequest, "Invalid URL")
	}

	u, err := url.Parse(req.URL)
	if err != nil {
		return c.String(http.StatusBadRequest, "Invalid URL")
	}

	if len(u.Scheme) > 6 || len(u.Scheme) < 3 {
		return c.String(http.StatusBadRequest, "Invalid URL scheme")
	}

	if slices.Contains(BLOCKED_PROTOCOLS, strings.ToUpper(u.Scheme)) {
		return c.String(http.StatusBadRequest, "Invalid URL scheme")
	}

	easy := curl.EasyInit()
	defer easy.Cleanup()

	easy.Setopt(curl.OPT_URL, req.URL)
	easy.Setopt(curl.OPT_TIMEOUT, 10)
	easy.Setopt(curl.OPT_VERBOSE, false)
	easy.Setopt(curl.OPT_MAXFILESIZE, 1024*10)

	var responseBody string
	easy.Setopt(curl.OPT_WRITEFUNCTION, func(buf []byte, _ interface{}) bool {
		responseBody += string(buf)
		return true
	})

	if err := easy.Perform(); err != nil {
		return c.String(http.StatusInternalServerError, "failed to make request")
	}

	statusCodeInt, err := easy.Getinfo(curl.INFO_RESPONSE_CODE)
	if err != nil {
		return c.String(http.StatusInternalServerError, "failed to make request")
	}

	statusCode, ok := statusCodeInt.(int)
	if !ok {
		return c.String(http.StatusBadRequest, "invalid status code")
	}

	if !slices.Contains(ALLOWED_STATUS_CODES, statusCode) {
		return c.String(http.StatusBadRequest, "Invalid status code: "+strconv.Itoa(statusCode)+"\nresp: "+responseBody)
	}

	var exists bool
	err = s.db.QueryRow(c.Request().Context(),
		"SELECT EXISTS(SELECT 1 FROM urls WHERE url = $1)", u.Host).Scan(&exists)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Database error: "+err.Error())
	}

	if exists {
		return c.String(http.StatusConflict, "Такой URL уже отправляли")
	}

	_, err = s.db.Exec(c.Request().Context(), "INSERT INTO urls (url) VALUES ($1)", u.Host)
	if err != nil {
		return c.String(http.StatusInternalServerError, "failed to insert URL")
	}

	userId, ok := c.Get("userId").(int)
	if !ok {
		return c.String(http.StatusUnauthorized, "User not authenticated")
	}

	login, ok := c.Get("login").(string)
	if !ok {
		return c.String(http.StatusUnauthorized, "User not authenticated")
	}

	if err := s.redis.Incr(c.Request().Context(), UrlCounterKey(userId, login)).Err(); err != nil {
		return c.String(http.StatusInternalServerError, "Redis error: "+err.Error())
	}

	return c.String(http.StatusOK, "Collect successful")
}

func ComparePassword(hashedPassword, password string) error {
	return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
}

func (s *Service) PostLogin(c echo.Context) error {
	type LoginRequest struct {
		Login    string `json:"login"`
		Password string `json:"password"`
	}

	var req LoginRequest
	if err := c.Bind(&req); err != nil {
		return c.String(http.StatusBadRequest, "Invalid request")
	}

	if req.Login == "" || req.Password == "" {
		return c.String(http.StatusBadRequest, "Invalid request")
	}

	var user User
	err := s.db.QueryRow(c.Request().Context(),
		"SELECT id, login, password FROM users WHERE login = $1;",
		req.Login).Scan(&user.UserId, &user.Login, &user.PasswordHash)
	if err != nil {
		return c.String(http.StatusUnauthorized, "Invalid credentials")
	}

	if err := ComparePassword(user.PasswordHash, req.Password); err != nil {
		return c.String(http.StatusUnauthorized, "Invalid credentials")
	}

	expirationTime := time.Now().Add(24 * time.Hour)
	claims := &Claims{
		Id:    user.UserId,
		Login: user.Login,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(JWT_SECRET)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Failed to generate token")
	}

	c.SetCookie(&http.Cookie{
		Name:    "token",
		Value:   tokenString,
		Expires: expirationTime,
		Path:    "/",
	})

	return c.String(http.StatusOK, "Login successful")
}

func HashPassword(password string) (string, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hash), nil
}

func (s *Service) PostSignup(c echo.Context) error {
	type SignupRequest struct {
		Login    string `json:"login"`
		Password string `json:"password"`
	}

	var req SignupRequest
	if err := c.Bind(&req); err != nil {
		return c.String(http.StatusBadRequest, "Invalid request")
	}

	if len(req.Login) < 6 {
		return c.String(http.StatusBadRequest, "Логин должен быть длиннее 6 символов")
	}

	if len(req.Password) < 12 {
		return c.String(http.StatusBadRequest, "Пароль должен быть длиннее 12 символов")
	}

	var exists bool
	err := s.db.QueryRow(c.Request().Context(),
		"SELECT EXISTS(SELECT 1 FROM users WHERE login = $1)", req.Login).Scan(&exists)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Database error")
	}
	if exists {
		return c.String(http.StatusConflict, "User already exists")
	}

	hashedPassword, err := HashPassword(req.Password)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Failed to hash password")
	}

	var userId int
	err = s.db.QueryRow(c.Request().Context(),
		"INSERT INTO users (login, password) VALUES ($1, $2) RETURNING id",
		req.Login, hashedPassword).Scan(&userId)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Failed to create user")
	}

	expirationTime := time.Now().Add(24 * time.Hour)
	claims := &Claims{
		Id:    userId,
		Login: req.Login,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(JWT_SECRET)
	if err != nil {
		return c.String(http.StatusInternalServerError, "Failed to generate token")
	}

	c.SetCookie(&http.Cookie{
		Name:    "token",
		Value:   tokenString,
		Expires: expirationTime,
		Path:    "/",
	})

	return c.String(http.StatusOK, "Signup successful")
}

func (s *Service) PostLogout(c echo.Context) error {
	c.SetCookie(&http.Cookie{
		Name:    "token",
		Value:   "",
		Expires: time.Now().Add(-1 * time.Hour),
		Path:    "/",
	})

	return c.String(http.StatusOK, "Logout successful")
}

func (s *Service) AuthMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		cookie, err := c.Cookie("token")
		if err != nil {
			return c.Redirect(http.StatusTemporaryRedirect, "/")
		}

		token, err := jwt.ParseWithClaims(cookie.Value, &Claims{}, func(token *jwt.Token) (interface{}, error) {
			if token.Method.Alg() != "HS256" {
				return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
			}
			return JWT_SECRET, nil
		})
		if err != nil {
			return c.Redirect(http.StatusTemporaryRedirect, "/")
		}

		if claims, ok := token.Claims.(*Claims); ok && token.Valid {
			c.Set("userId", claims.Id)
			c.Set("login", claims.Login)
			return next(c)
		}
		return c.Redirect(http.StatusTemporaryRedirect, "/")
	}
}
