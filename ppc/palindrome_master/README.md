# palindrome master | medium | ppc

## Информация

> А вы любите палиндромы? Вам предстоит из данного вам списка слов составить один палиндром. Все слова должны быть использованы. Слова нельзя изменять. Если слов несколько, они должны быть разделены пробелами.
>
> Example:
>
> ```
> Round 1:
> lprerystofrcbyhzygjtveeaugvtovkybarmgrdughymfceaglajevjxtpqdaqfs sfqadqptxjvejalgaecfmyhgudrgmrabykvotvguaeevtjgyzhybcrfotsyrerplgtvv vvtg
> Your answer: sfqadqptxjvejalgaecfmyhgudrgmrabykvotvguaeevtjgyzhybcrfotsyrerplgtvv vvtg lprerystofrcbyhzygjtveeaugvtovkybarmgrdughymfceaglajevjxtpqdaqfs
> ```
>
> слова  `sfqadqptxjvejalgaecfmyhgudrgmrabykvotvguaeevtjgyzhybcrfotsyrerplgtvv vvtg lprerystofrcbyhzygjtveeaugvtovkybarmgrdughymfceaglajevjxtpqdaqfs` при конктенации образуют палиндром `sfqadqptxjvejalgaecfmyhgudrgmrabykvotvguaeevtjgyzhybcrfotsyrerplgtvvvvtglprerystofrcbyhzygjtveeaugvtovkybarmgrdughymfceaglajevjxtpqdaqfs`
>
> ```
> nc ip:5000
> ```

## Деплой

```
cd deploy
docker compose up --build -d
```

## Выдать участинкам

ip:port

## Описание

Составляем палиндром из данных слов. Тупо перебором пермутейшенсов слов

## Решение

[Эксплоит](solve/solve.py)

## Флаг

```
ozonctf{4_15_7h3_b357_3n6l15h_p4l1ndr0m3}
```
