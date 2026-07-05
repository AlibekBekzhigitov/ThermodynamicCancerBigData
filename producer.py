import csv
import json
import os
import time
from kafka import KafkaProducer

# 1. Automically determine the base directory of the project (two levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Define the path to the CSV file containing genetic data
#  path: /path/to/your/project/data/CCLE_gene_cn.csv
CSV_FILE_PATH = os.path.join(BASE_DIR, 'data', 'CCLE_gene_cn.csv')

# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'biomolecules-stream'


def create_producer():
    """Initialize and return a Kafka producer instance."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        # Translate Python dict to JSON string and then to bytes for Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


def stream_genetic_data():
    producer = create_producer()
    print(f"[*] Producer started. Sending data to topic '{KAFKA_TOPIC}'...")

    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            #  Read CSV file as a dictionary, where each row is a dict with column headers as keys
            reader = csv.DictReader(file)

            counter = 0
            for row in reader:
                #  retrieve ID of the cell line from the current row
                cell_line_id = row.get('DepMap_ID') or row.get('')

                # Send the row data to Kafka topic
                producer.send(KAFKA_TOPIC, value=row)

                counter += 1
                if counter % 10 == 0:
                    print(f"[->] Sent {counter} cell line profiles (microsystems)...")

                # Imitation of sending data in real-time, with a small delay between messages.
                # 0.5 sec delay to simulate real-time streaming of data
                time.sleep(0.5)

    except FileNotFoundError:
        print(f"[!] Error: File not found at path {CSV_FILE_PATH}")
        print("Please check that the file CCLE_gene_cn_v3.csv exists in the 'data' folder and is named correctly.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        # Safely close the network connections
        producer.flush()
        producer.close()
        print("[*] Producer stopped.")


if __name__ == '__main__':
    stream_genetic_data()