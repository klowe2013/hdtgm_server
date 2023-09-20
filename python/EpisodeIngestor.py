import base64
import re 
from imdb import Cinemagoer 
import uuid 
import json 
from python.CassandraInterface import CassandraInterface 

class EpisodeIngestor:
    media_dir = './media/audio_files/'
    KEYSPACE = 'hdtgm_episodes'
    TABLE = 'audio_binary'
    # TODO: update CASS_SCHEMA with new IMDB info
    CASS_SCHEMA = '(id text, filename text, binary text, PRIMARY KEY (id))'
        
    def __init__(self):
        self.episode_name = ''
        self.cassandra = CassandraInterface(self.KEYSPACE)
        self.imdb = Cinemagoer()
        self.imdb_info = {}

    def _write_cassandra(self, data):
        print(f'Writing ID {data["id"]} ({data["filename"]}) to Cassandra')
        
        rows = self.cassandra.write_cassandra(data, self.TABLE)
        return rows 
    
    def _create_cassandra(self):
        self.cassandra.create_table(self.TABLE, self.CASS_SCHEMA)

    @staticmethod
    def parse_title(filename):
        cut_strings = ['.mp3', 'LIVE!', 'LIVE']

        title_str = filename
        if ')' not in title_str and '(' in title_str:
            title_str = title_str.replace('.mp3', ').mp3')

        # Remove everything up to first letter
        title_str = re.sub('^[^A-Za-z]+', '', title_str)
        title_str = re.sub('\([^)]*\)', '', title_str)
        for c in cut_strings:
            title_str = title_str.replace(c, '')
        return title_str 
    
    @staticmethod
    def get_episode_no(filename):
        # Get episode number from title
        episode_no = re.search('(^([0-9]+))', filename).group(0)
        return episode_no
    
    @staticmethod
    def _search_title(imdb, title_str):
        
        search_results = imdb.search_movie(title_str.strip())
    
        check_ind, found_movie = 0, False
        while check_ind < len(search_results) and not found_movie:
            first_movie = imdb.get_movie(search_results[check_ind].getID())    
            if 'plot' in first_movie.keys():
                found_movie = True
            else:
                check_ind += 1
        
        # If it couldn't be found, or if it's a TV show (number of episodes), skip
        # Later, let's replace the search results query with a fuzzy match, and if match < thresh skip
        if check_ind == len(search_results) or 'number of episodes' in first_movie.keys():
            imdb_info = {}
        else:
            cast = first_movie.get('cast')
            cast = [str(c) for c in cast[:(min(3, len(cast)))]]
            imdb_info = {
                'imdb_title': first_movie['title'],
                'genres': first_movie['genres'],
                'description': first_movie['plot outline'] if 'plot outline' in first_movie.keys() else first_movie['plot'],
                'rating': first_movie.get('rating', -1),
                'year': first_movie['year'],
                'cast': cast
            }
        return imdb_info 
    
    
    def ingest(self, episode_name, initialize=True):
        
        # Get title, episode number, ID
        internal_id = str(uuid.uuid4())
        
        # Get title and episode number
        title = self.parse_title(episode_name)
        episode_no = self.get_episode_no(episode_name)

        # Get IMDB Info
        imdb_info = self._search_title(self.imdb, title)

        all_info = {
            'id': internal_id,
            'filename': episode_name,
            'title': title,
            'episode_no': episode_no
        }
        for k, v in imdb_info.items():
            all_info[k] = v

        # Write audio data to Cassandra
        if initialize:
            self._create_cassandra()
        self._write_cassandra(all_info)

        
