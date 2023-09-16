import base64
import re 
from imdb import Cinemagoer 
import uuid 
from kafka import KafkaProducer 
import json 
from python.CassandraWriter import CassandraWriter 

class EpisodeIngestor:
    media_dir = './media/audio_files/'
    KEYSPACE = 'hdtgm_episodes'
    TABLE = 'audio_binary'
    def __init__(self, episode_name):
        self.episode_name = episode_name 
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092', 
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )


    def _get_binary(self):
        with open(f"{self.media_dir}/{self.episode_name}", 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('UTF-8')
        return audio_data
    
    def publish_kafka(self, id):
        kafka_data = {
            'id': id,
            'filename': self.episode_name,
        }

        self.producer.send("uploaded_files", kafka_data)
        self.producer.flush()
        self.producer.close()

    def _write_cassandra(self, data):
        pass
    
    def ingest(self):
        # Get title, episode number, ID
        internal_id = str(uuid.uuid4())
        
        # Get binary data
        audio_data = self._get_binary()

        # Write audio data to Cassandra
        self._write_cassandra({'id': internal_id, 'filename': self.episode_name, 'binary': audio_data})

        # Publish ID and filename to Kafka topic for batch IMDB parsing
        self.publish_kafka(internal_id)
