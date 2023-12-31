import base64
import re 
from imdb import Cinemagoer 
import uuid 
import json 
from python.db_interfaces.DatabaseFactory import DatabaseFactory 
from python.constants import SQLITE_EPISODE_SCHEMA, SQLITE_DB, EPISODE_INFO
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("episode_ingestion")


class EpisodeIngestor:
    media_dir = './media/audio_files/'
    DATABASE = SQLITE_DB
    INFO_TABLE = EPISODE_INFO
        
    def __init__(self):
        self.episode_name = ''
        self.database = DatabaseFactory(self.DATABASE).create('sqlite')
        self.imdb = Cinemagoer()
        self.imdb_info = {}

    def _write_entry(self, data, table):
        print(f'Writing ID {data["id"]} ({data["filename"]}) to DB')
        
        rows = self.database.write_entry(data, table)
        return rows 
    
    def _create_table(self, table, schema):
        self.database.create_table(table, schema)

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
                'description': first_movie['plot outline'] if 'plot outline' in first_movie.keys() else first_movie['plot'][0],
                'rating': first_movie.get('rating', -1),
                'year': first_movie['year'],
                'cast': cast
            }
        return imdb_info 
    
    
    def ingest(self, internal_id, episode_name, initialize=True):
        
        # TODO: get episode_name from internal_id lookup
        # episode_name = self._get_name_from_id(internal_id)
        
        # Get title and episode number
        title = self.parse_title(episode_name)
        episode_no = self.get_episode_no(episode_name)

        logging.info(f'parsed episode {episode_name} into episode #{episode_no}: {title}')

        # Get IMDB Info
        try:
            imdb_info = self._search_title(self.imdb, title)
            logging.info(imdb_info)
        except BaseException as e:
            imdb_info = {}
            logging.info(f"Failed to find {title} on IMDB: {e}")

        all_info = {
            'id': internal_id,
            'filename': episode_name,
            'title': title,
            'episode_no': episode_no,
            'imdb_title': '',
            'genres': '',
            'description': '',
            'rating': -1,
            'year': 0000,
            'cast': ''
        }

        # Add IMDB Info
        for k, v in imdb_info.items():
            if k in ['genres', 'cast']:
                all_info[k] = ', '.join(v)
            else:
                all_info[k] = v
        
        # Write audio data to DB
        # TODO: Move the initialization to an init script
        if initialize:
            self.database.create_table(self.INFO_TABLE, SQLITE_EPISODE_SCHEMA)
        rows = self.database.write_entry(all_info, self.INFO_TABLE)


        
