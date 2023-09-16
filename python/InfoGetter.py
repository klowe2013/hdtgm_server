from imdb import Cinemagoer 
import re 

class InfoGetter:

    def __init__(self):
        self.imdb = Cinemagoer()
        self.imdb_info = {}

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
    
    def _search_title(self):
        title_str = self.parse_title(self.episode_name)

        search_results = self.imdb.search_movie(title_str.strip())
    
        check_ind, found_movie = 0, False
        while check_ind < len(search_results) and not found_movie:
            first_movie = self.imdb.get_movie(search_results[check_ind].getID())    
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
        self.imdb_info = imdb_info
        return imdb_info 
    