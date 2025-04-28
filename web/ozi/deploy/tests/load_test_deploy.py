#!/usr/bin/env python3
import requests
import uuid
import time

# Адрес сервера
base_url = "http://92.42.96.224:2169"
# base_url = "http://127.0.0.1:2169"

# Заголовки для GET и POST запросов
headers = {
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

for _ in range(40): 
    # Создаем новую сессию
    session = requests.Session()

    # Шаг 1: GET-запрос на /
    index_response = session.get(f"{base_url}/", headers=headers)

    # Получаем user_uuid из куки
    user_uuid = session.cookies.get("user_uuid")
    
    if user_uuid:
        print(f"[+] Получен user_uuid: {user_uuid}")
        
        # Шаг 2: POST-запрос на /deploy с этим UUID
        post_headers = headers.copy()
        post_headers["Content-Type"] = "application/json"
        post_headers["Origin"] = base_url
        post_headers["Referer"] = f"{base_url}/"
        
        data = {
            "key": "value"  # Добавь сюда нужные данные для POST-запроса
        }
        
        deploy_response = session.post(f"{base_url}/deploy", headers=post_headers, cookies={"user_uuid": user_uuid}, json=data)
        print(f"[{user_uuid}] POST /deploy -> Status: {deploy_response.status_code}")
    else:
        print("[-] Сервер не вернул user_uuid :(")

    time.sleep(0.2)  # Пауза между итерациями


