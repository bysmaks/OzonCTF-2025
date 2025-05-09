# Serpent's Hidden Path | легкий/средний? | web

## Информация

"Скрытый лабиринт змеи ведёт к секретному пути. Сможете ли вы найти его?"

"Очередное точное и четкое описание, куда доставить заказ", - сказал Гоша

https://snake.web.ozon-ctf-2025.ru/

Внимание! Задание разворачивается в режиме per-instance. Атаковать деплоер не нужно!

## Деплой

```sh
cd deploy
./deploy.sh
```
> [ВАЖНО]
> Проверьте .env файл в deploy директории. Нужно убедиться что параматры портов `START_RANGE` `STOP_RANGE` `FLASK_APP_PORT` `DIRECT_TEST_PORT` и параметры сети `NETWORK_SUBNET`
> Не пересекаются с другими портами/подсетями на хостовой операционной системе. При необходимости можно отредактировать эти параметры.
> Задание не будет кореектно работать, если деплоер будет доступен по ссылке с доменного имени, а не IP адреса. 
> Если вы планируете использовать доменное имя при доступе к деплоеру, то необходимо прописать его в snake_game/conf.d/90-decoy.conf 
> пример (90-decoy.conf) line:6 `server_name localhost 127.0.0.1 OZONCTF.RU "" ~^\d+\.\d+\.\d+\.\d+$;`
## Выдать участникам

Адрес сервиса и текст из раздела "Информация".

## Описание

"Serpent's Hidden Path" - это веб-CTF задание, построенное вокруг классической игры "Змейка", реализованной с использованием NGINX и Lua. На первый взгляд, это обычная игра, где участники должны набирать очки, управляя змейкой. Однако настоящая цель - эксплуатировать особенности обработки маршрутов в NGINX и использовать нестандартные HTTP-методы для обнаружения скрытого флага.

Флаг разделен на три части, каждая из которых требует своего метода обнаружения. Этот многоуровневый подход проверяет понимание участниками конфигураций веб-сервера, протоколов HTTP и внимание к деталям.

### Основной механизм: поведение NGINX при выборе сервера по умолчанию

Задание использует специфическое поведение NGINX при обработке виртуальных хостов:

**Поведение NGINX для несуществующих хостов**:
1. Когда NGINX получает запрос для хоста, не соответствующего ни одной директиве `server_name`, он следует определенному алгоритму для определения, какой блок сервера должен обрабатывать запрос.
2. Многие полагают, что блок сервера с параметром `default_server` всегда будет выбран, но это верно только если ни один из предыдущих блоков не был обработан.
3. **Ключевой момент**: Если ни один `default_server` явно не задан среди соответствующих блоков сервера, NGINX использует **первый блок сервера**, определенный для данной комбинации IP:порт.
4. "Первый блок сервера" определяется **порядком загрузки файлов** при использовании нескольких включенных файлов конфигурации.
5. Файлы в `conf.d/` загружаются в **алфавитном порядке** - так что `20-prize.conf` загружается раньше, чем `90-decoy.conf`, независимо от того, какой из них имеет `default_server`.

Это поведение создает ситуацию, когда участники думают, что взаимодействуют с одним сервером, но на самом деле получают доступ к совершенно другому при использовании определенных техник.

## Решение
### TL;DR
```bash 
echo "{server_ip} snake.ctf.local" >> /etc/hosts
echo "{server_ip} nonexistent.domain" >> /etc/hosts
./test_flags.sh nonexistent.domain {port}
```

### Этап 1: Начальное исследование

1. Участник открывает предоставленный URL и находит стандартную игру "Змейка"
2. Проверив исходный код, он может заметить подсказки о "неправильном сервере" и "заголовках хоста"
3. Дальнейшее исследование сайта выявляет конечную точку `/hint` с загадочными сообщениями

### Этап 2: Обнаружение секретного сервера

Участник должен понять, что нужно попробовать обратиться к сайту с:
- Пустым заголовком Host: `curl -H "Host:" http://{ip}:9000/snake`
- Недействительным именем хоста: `curl -H "Host: nonexistent.domain" http://{ip}:9000/snake`
- Прямым IP: `curl http://{ip}:9000/snake` (без установки Host в некоторых клиентах)

Это приведет его к секретной версии игры "Змейка", которая выглядит похоже, но содержит золотые яйца, при наборе определённого количества, участнику откроется часть флага

### Этап 3: Сбор специальных предметов

В секретной игре "Змейка":
1. Участник замечает золотые яблоки, которые появляются вместе с обычной едой
2. Нужно управлять змейкой, чтобы собрать эти специальные предметы
3. После сбора 3 специальных предметов игрок получает среднюю часть флага: `default_server_first_`
4. Игра также предлагает проверить `/flag-piece` с разными HTTP-методами

### Этап 4: Вариации HTTP-методов

Основываясь на подсказках:
1. Участник пробует разные HTTP-методы на конечной точке `/flag-piece`:
   - OPTIONS: `curl -X OPTIONS http://{ip}:9000/flag-piece -I`
   - HEAD: `curl -I http://{ip}:9000/flag-piece`
   - (Не забывая использовать несуществующий хост или пустой заголовок Host)

2. Эти запросы обнаруживают:
   - Метод OPTIONS: `X-Flag-Part-1: OzonCTF{nginx_`
   - Метод HEAD: `X-Flag-Part-3: alphabetical}`

### Этап 5: Сборка флага

Участник объединяет все три части, чтобы сформировать полный флаг:
`OzonCTF{nginx_default_server_first_alphabetical}`

## Инструменты для решения

Участникам понадобятся:
1. **curl** - Для создания собственных HTTP-запросов с определенными заголовками и методами
2. **Инструменты разработчика браузера** - Для проверки заголовков и ответов
3. **Расширения браузера** - Такие как ModHeader для Firefox/Chrome для изменения заголовков запросов
4. **Знание HTTP** - Понимание различных HTTP-методов и заголовков
5. **Игровые навыки** - Базовая способность играть в "Змейку" и собирать специальные предметы

## Флаг

`OzonCTF{nginx_default_server_first_alphabetical}`

