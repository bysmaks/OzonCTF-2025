import paho.mqtt.client as mqtt
import time
import random
import json
from datetime import datetime
import os

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_DATA_TOPIC = os.getenv("MQTT_DATA_TOPIC")
MQTT_RESPONSE_TOPIC = os.getenv("MQTT_RESPONSE_TOPIC")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def send_sensor_data():
    client = mqtt.Client()

        # Установка логина и пароля
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    # Подключение к брокеру
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Генерация данных
    temperature = random.uniform(20.0, 30.0)
    light_level = random.uniform(0.0, 100.0)
    network_status = random.choice(["Connected", "Disconnected"])
    timestamp = datetime.now().isoformat()

    data = {
        "temperature": temperature,
        "light_level": light_level,
        "network_status": network_status,
        "timestamp": timestamp
    }
    message = json.dumps(data)

    client.publish(MQTT_DATA_TOPIC, message)
    print(f"Sent data: {message}")

    def on_message(client, userdata, msg):
        response = msg.payload.decode()
        try:
            response_data = json.loads(response)
            if "status" in response_data and response_data["status"] in ["OK", "ERROR"]:
                print(f"Received response: {response_data}")
        except json.JSONDecodeError:
            print(f"Received invalid response: {response}")

    client.subscribe(MQTT_RESPONSE_TOPIC)
    client.on_message = on_message

    client.loop_start()
    time.sleep(0.5)
    client.loop_stop()

    client.disconnect()

if __name__ == "__main__":
    while True:
        send_sensor_data()
        time.sleep(1)
