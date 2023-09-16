import base64
import re 
from imdb import Cinemagoer 
import uuid 
from kafka import KafkaProducer 
import json 
from ..python.CassandraWriter import CassandraWriter 

class EpisodeIngestor:
    media_dir = '.'
    KEYSPACE = 'hdtgm_episodes'
    TABLE = 'audio_binary'
    def __init__(self, episode_name):
        self.episode_name = episode_name 
        self.producer = KafkaProducer(bootstrap_servers=['kafka1:19092', 'kafka2:19093', 'kafka3:19094'])
        self.writer = CassandraWriter(self.KEYSPACE, self.TABLE)

    def _get_binary(self):
        with open(f"{self.media_dir}/{self.episode_name}", 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('UTF-8')
        return audio_data
    
    def publish_kafka(self, id):
        kafka_data = {
            'id': id,
            'filename': self.episode_name,
        }

        self.producer.send("random_names", json.dumps(kafka_data).encode('utf-8'))
    
    def ingest(self):
        # Get title, episode number, ID
        internal_id = uuid.uuid4()
        
        # Get binary data
        audio_data = self._get_binary()

        # Write audio data to Cassandra
        self.write_cassandra({'id': internal_id, 'filename': self.episode_name, 'binary': audio_data})

        # Publish ID and filename to Kafka topic for batch IMDB parsing
        self.publish_kafka(internal_id)

        # Get title and episode number
        title = self.parse_title(self.episode_name)
        episode_no = self.get_episode_no(self.episode_name)

        # Get IMDB Info
        imdb_info = self._search_title()
