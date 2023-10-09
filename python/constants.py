from string import Template

CASSANDRA_FILE_SCHEMA = '(id text, filename text, binary text, PRIMARY KEY (id))'
SQLITE_EPISODE_SCHEMA = """
(ID    TEXT    PRIMARY KEY    NOT NULL,
FILENAME     TEXT    NOT NULL, 
EPISODE_NO  INT NOT NULL,
TITLE   TEXT    NOT NULL,
IMDB_TITLE  TEXT,
YEAR    INT,
DESCRIPTION TEXT,
RATING  REAL,
GENRES   TEXT,
CAST    TEXT
)
"""

SQLITE_FILEPATH_SCHEMA = """
(ID    TEXT    PRIMARY KEY    NOT NULL,
FILEPATH     TEXT    NOT NULL
)
"""

SQLITE_DB = 'hdtgm_database_gc.db'
EPISODE_INFO = 'episode_info'
FILE_PATH_TABLE = 'episode_paths'

GCLOUD_PREFIX = 'hdtgm-episodes'
MEDIA_FOLDER = './data/media/audio_files'
