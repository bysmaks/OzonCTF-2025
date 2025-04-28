# v8_hell | HARD | PWN

## Информация

In ancient code, the flaws reside, Old vulnerabilities, silent, deep, Through years they linger, never hide, Awaiting moments their watch to keep.

Посмотрите, какой красивый стих сочинил Гоша, возможно он натолкнет вас на какую-то мысль...

nc pwn.ozon-ctf-2025.ru 13337

## Деплой

```sh
cd deploy
docker-compose up --build -d
```

## Выдать участинкам

Архив из директории [public/](public/) и IP:PORT сервера

## Описание

Чейн v8 memory corruption + v8 sandbox bypass в v8 от июня  2024(чейнить две 1-day)

## Решение

[Эксплоит](solve/sploit.py)

## Флаг

`ozonctf{15_17_345y_70_3xpl017_1d4y_ch41n}`
