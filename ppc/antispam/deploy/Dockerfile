FROM rust:1.85.1-alpine as builder

RUN apk add --no-cache musl-dev protoc

WORKDIR /usr/src/ozon
COPY . .

RUN cargo build --release

FROM alpine

WORKDIR /usr/local/bin
COPY --from=builder /usr/src/ozon/target/release/ozon .

CMD ["ozon"]