import json
import random
from datetime import datetime, timedelta

from paho.mqtt import publish

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC = "agrotrace/telemetry"

def generate_telemetry_batch(shipment_id: int, num_readings: int = 100):
    readings = []
    base_time = datetime.utcnow() - timedelta(minutes=num_readings)
    
    for i in range(num_readings):
        readings.append({
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "temperature": random.randint(-20, -10),
            "humidity": random.randint(40, 60),
            "gps": f"{-23.5505 + (i * 0.001)},{-46.6333 + (i * 0.001)}"
        })
        
    return {
        "shipment_id": shipment_id,
        "readings": readings
    }

if __name__ == "__main__":
    shipment_id = 1 # Assuming a shipment with ID 1 exists
    print(f"Generating batch of 500 telemetry readings for shipment {shipment_id}...")
    payload = generate_telemetry_batch(shipment_id, 500)
    
    print("Publishing to MQTT broker...")
    publish.single(TOPIC, payload=json.dumps(payload), hostname=MQTT_BROKER, port=MQTT_PORT)
    print("Published successfully!")
