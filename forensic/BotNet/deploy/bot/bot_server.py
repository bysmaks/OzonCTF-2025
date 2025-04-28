import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os

# Настройки MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_DATA_TOPIC = os.getenv("MQTT_DATA_TOPIC")
MQTT_RESPONSE_TOPIC = os.getenv("MQTT_RESPONSE_TOPIC")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode()
        data = json.loads(message)
        print(f"Received data: {data}")

        # Проверка данных
        if all(key in data for key in ["temperature", "light_level", "network_status", "timestamp"]):
            status = "OK"
        else:
            status = "ERROR"

        response_data = {
            "status": status,
            "server_id": "Smart_home",
            "timestamp": datetime.now().isoformat()
        }
        response = json.dumps(response_data)

        # Отправка подтверждения
        client.publish(MQTT_RESPONSE_TOPIC, response)
        print(f"Sent response: {response}")

    except json.JSONDecodeError:
        response_data = {
            "status": "ERROR",
            "server_id": "Server1",
            "timestamp": datetime.now().isoformat()
        }
        response = json.dumps(response_data)
        client.publish(MQTT_RESPONSE_TOPIC, response)
        print(f"Sent response: {response}")

client = mqtt.Client()

if MQTT_USER and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(MQTT_DATA_TOPIC)

client.loop_forever()
