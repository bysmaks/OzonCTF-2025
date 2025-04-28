import paho.mqtt.client as mqtt
import time
import json
import base64
from datetime import datetime
import os

# Настройки MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_RESPONSE_TOPIC = os.getenv("MQTT_RESPONSE_TOPIC")
ATTACK_STRING = os.getenv("ATTACK_STRING")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def send_attack_message():
    client = mqtt.Client()
    
    # Установка логина и пароля
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Создание JSON сообщения
    attack_data = {
        "status": "ATTACK",
        "server_id": "povolze_ctf",
        "timestamp": datetime.now().isoformat(),
        "attack": base64.b64encode(ATTACK_STRING.encode()).decode()
    }
    message = json.dumps(attack_data)

    client.publish(MQTT_RESPONSE_TOPIC, message)
    print(f"Sent attack message: {message}")

    # Отключение от брокера
    client.disconnect()

if __name__ == "__main__":
    while True:
        send_attack_message()
        time.sleep(60)
