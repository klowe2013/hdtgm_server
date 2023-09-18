import base64
import re 
from imdb import Cinemagoer 
import uuid 
from kafka import KafkaProducer 
import json 
from python.CassandraInterface import CassandraInterface 

class EpisodeIngestor:
    media_dir = './media/audio_files/'
    KEYSPACE = 'hdtgm_episodes'
    TABLE = 'audio_binary'
    CASS_SCHEMA = '(id text, filename text, binary text, PRIMARY KEY (id))'
        
    def __init__(self):
        self.episode_name = ''
        # self.producer = KafkaProducer(
        #     bootstrap_servers='localhost:9092', 
        #     value_serializer=lambda x: json.dumps(x).encode('utf-8')
        # )
        self.cassandra = CassandraInterface(self.KEYSPACE)

    def _publish_kafka(self, id):
        kafka_data = {
            'id': id,
            'filename': self.episode_name,
        }
        print(f'publishing {kafka_data} to Kafka stream')

        self.producer.send("uploaded_files", kafka_data)
        self.producer.flush()
        self.producer.close()
        return kafka_data

    def _write_cassandra(self, data):
        print(f'Writing ID {data["id"]} ({data["filename"]}) to Cassandra')
        
        rows = self.cassandra.write_cassandra(data, self.TABLE)
        return rows 
    
    def _create_cassandra(self):
        self.cassandra.create_table(self.TABLE, self.CASS_SCHEMA)
    
    def ingest(self, episode_name, initialize=True):
        
        # Get title, episode number, ID
        internal_id = str(uuid.uuid4())
        
        # Get binary data
        with open(f"{self.media_dir}/{episode_name}", 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('UTF-8')

        # Write audio data to Cassandra
        if initialize:
            self._create_cassandra()
        self._write_cassandra({'id': internal_id, 'filename': episode_name, 'binary': audio_data})

        # Publish ID and filename to Kafka topic for batch IMDB parsing
        # self._publish_kafka(internal_id)
