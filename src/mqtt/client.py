import logging

import paho.mqtt.client as mqtt

from src.mqtt.handler import process_handshake_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
HANDSHAKE_TOPIC = "agrotrace/handshake"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(HANDSHAKE_TOPIC)
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    logger.info(f"Received message on {msg.topic}")
    process_handshake_message(msg.payload)

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        logger.error(f"Could not connect to MQTT: {e}")
    return client
