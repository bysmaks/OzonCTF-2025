# odin raz ne Weierstrass | hard | crypto

## Информация

Гоша обнаружил аномалию в одной из межзвездных посылок. Вместо ожидаемого груза — зашифрованные данные, которые не поддаются стандартной расшифровке логистических дронов.

Система маршрутизации показывает, что посылка проходила через подозрительную червоточину в секторе EC-Curve-256, известном своими гравитационными аномалиями, влияющими на передачу данных.

Сможешь расшифровать эту посылку?

## Деплой

```
не предусмотрен  
```

## Выдать участинкам

Файлы из директории public/

## Описание

Приколы с кривыми эллиптическими кривыми.

## Решение

Замечаем, что автор написал класс для EC -> Осознаем что что-то не так -> Задача сводится к работе с эллиптическими кривыми над $\mathbb{Z}/pq\mathbb{Z}$. Вычисляем дискриминант $\Delta = 0$ -> кривые вырождены -> ФТГ -> Находим $p, q$ через $\gcd(c_4, N)$ Решаем DLP в $\mathbb{F}_p(\sqrt{\alpha})^*$ и $\mathbb{F}_q^+$. Восстанавливаем флаг через КТО.

## Флаг

```
ozonctf{b0741_4l63bru_4nd_kryp706r4f1yu_4nd_b3_c00l_45_d1m4}
```
