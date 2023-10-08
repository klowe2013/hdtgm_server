from python.constants import EPISODE_INFO, SQLITE_DB
from python.db_interfaces.DatabaseFactory import DatabaseFactory
from string import Template 

class EpisodeCard:

    CARD_TEMPLATE = Template(
"""
<div class="card-title">
    <p><b>#${episode_no}: ${imdb_title}</b></p>
    <p><b>Starring:</b> ${cast}</p>
    <p><b>Genres:</b> ${genres}</p>
    <p>${description}</p>
</div>
"""
)
    def __init__(self, episode_id, database=None):
        self.episode_id = episode_id
        self.database = database
        if self.database is None:
            self.database = DatabaseFactory(SQLITE_DB).create('sqlite')

    def get_card_info(self):
        episode_info = self.database.query(f"""
            select id, episode_no, imdb_title, year, description, rating, genres, `cast` from {EPISODE_INFO} 
            where id = "{self.episode_id}"
            """)
        episodes_dict = {k.lower(): v[0] for k, v in episode_info.to_dict(orient='list').items()}
        return episodes_dict 
    
    def get_div(self):
        episodes_dict = self.get_card_info()
        return self.CARD_TEMPLATE.substitute(episodes_dict)
        