# Этап сборки
FROM golang:1.23-bookworm AS builder

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git build-essential pkg-config libcurl4-openssl-dev

WORKDIR /app

# Копируем go.mod и go.sum для загрузки зависимостей
COPY go.mod go.sum ./
RUN go mod download

# Копируем остальной код (кроме игнорируемых файлов)
COPY . .

# Собираем приложение
RUN CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build -o main .

ENTRYPOINT ["./main"]