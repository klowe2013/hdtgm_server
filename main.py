from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import base64 
import glob 
import json 
import numpy as np 
from fuzzywuzzy import fuzz 
import numpy as np 
import redis 
import time 
import os 
from python.EpisodeIngestor import EpisodeIngestor
from python.db_interfaces.DatabaseFactory import DatabaseFactory
from python.constants import SQLITE_DB, EPISODE_INFO, FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA
from google.cloud import storage 
import requests 
import uuid 
import sys 

# from constants import REDIS_IP, REDIS_PORT
REDIS_IP, REDIS_PORT = os.getenv('REDIS_IP', '172.17.0.1'), 6379

r = 1 #redis.Redis(host=REDIS_IP, port=REDIS_PORT, decode_responses=True)
try: 
    r.set('up_check', 'up')
except:
    r = 1
app = Flask(__name__)

# BASE_DIR = '/hdtgm-player/media/audio_files/'
BASE_DIR = '/Users/kaleb/Documents/gitRepos/Projects/Hdtgm_webserver/media/audio_files/'
# BASE_DIR = '/Users/kaleb/Documents/HDTGM Episodes/'
# BASE_DIR = '/home/pi/Documents/hdtgm_server/media/audio_files/audio_files/'
# all_files = glob.glob(f'{BASE_DIR}/*')
# all_filenames = sorted([f.split('/')[-1] for f in all_files])
# all_titles = [f.replace('_', '') for f in all_filenames]

global bucket, blobs, all_filenames, all_titles
BASE_BUCKET = 'hdtgm-episodes'
client = storage.Client(project='hdtgm-player')
bucket = client.bucket(BASE_BUCKET)

database = DatabaseFactory(SQLITE_DB).create('sqlite')
    
@app.route('/')
def index():
    return redirect('/search')

def get_all_titles():
    # blobs = client.list_blobs(BASE_BUCKET)
    # all_filenames = sorted([blob.name for blob in blobs])
    # # all_titles = [f.replace('_', '') for f in all_filenames]
    all_filenames = [
        str(v) 
        for v in database.query(f'select distinct(imdb_title) from {EPISODE_INFO}')['IMDB_TITLE'].values
    ]
    return all_filenames

@app.route('/player')
def player():
    all_titles = get_all_titles()
    template_data = {
        'title': 'HDTGM Episode Player',
        'episodes': {ie: episode for ie, episode in enumerate(all_titles)}
    }
    return render_template('player.html', **template_data)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    template_data = {
        'title': 'HDTGM Episode Lookup',
        'episodes': {}
    }
    return render_template('search_page.html', **template_data)

@app.route('/search_text', methods=['GET', 'POST'])
def search_text():
    # Check for params
    try:
        request_params = request.get_json()
    except:
        request_params = {}

    search_text = request_params.get('search_text', '')
    n_results = int(request_params.get('n_results', '5'))

    try:
        title_pd = database.query(f'select id, imdb_title from {EPISODE_INFO}')
    except BaseException as e:
        print(f"Failed to query episode info table: {str(e)}")
        all_titles, all_ids = [], []
    
    if title_pd is None:
        all_titles, all_ids = [], []
    else:
        all_titles, all_ids = title_pd['IMDB_TITLE'].values, title_pd['ID'].values
    
    fuzzy_match_ratios = np.array([fuzz.partial_ratio(search_text, f) for f in all_titles])
    match_inds = np.argsort(fuzzy_match_ratios)[::-1]
    search_data = {
        'episodes': {all_ids[match]: all_titles[match] for match in match_inds[:n_results]}
    }
    
    res = app.response_class(response=json.dumps(search_data),
        status=200,
        mimetype='application/json')
    return res


@app.route('/audio_by_id/<string:id>')
def get_audio_by_id(id):
    
    print(f'pulling audio for id {id}')
    # TODO: Request gets numerical 1-n ID, not new unique internal ID.
    # Update request (probably in JS files?) to account for this

    # Default to pull from Redis cache
    start_time = time.time()
    if hasattr(r, 'set'):
        # Get audio data, or return None if not in redis
        audio_data = r.get(f'audio_data:{id}')
    else:
        # Default to None for next conditional check
        audio_data = None 

    if audio_data is None:
        # Get path to file
        this_file = database.query(
            f"""
            select FILEPATH from {FILE_PATH_TABLE} 
            where id=='{id}'
            """
        )['FILEPATH'].values[0]

        # with open(f"{BASE_DIR}/{this_file}", 'rb') as f:
        with open(this_file, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('UTF-8')
            print(f'Loaded data from source file in {time.time()-start_time:.2f}s: {audio_data[:100]}')
            if hasattr(r, 'set'): r.set(f'audio_data:{id}', audio_data)
        # audio_blob = bucket.blob(f"{all_filenames[id]}")
        # with audio_blob.open('rb') as f:
        #     audio_data = base64.b64encode(f.read()).decode('UTF-8')
        #     print(f'Loaded data from source file in {time.time()-start_time:.2f}s')
        #     if hasattr(r, 'set'): r.set(f'audio_data:{id}', audio_data)
    else:
        print(f'Loaded data from cache in {time.time()-start_time:.2f}s')

    data = {"snd": audio_data}
    res = app.response_class(response=json.dumps(data),
        status=200,
        mimetype='application/json')
    return res

@app.route('/episode_upload', methods=['GET', 'POST'])
def episode_upload():
    ingestor = EpisodeIngestor()
    
    upload_folder = './media/audio_files'
    uploaded_files = request.files.getlist('file')
    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(upload_folder, filename))

        # Get title, episode number, ID
        internal_id = str(uuid.uuid4())
        # TODO: Write table ID -> storage location
        id_info = {
            'id': internal_id,
            'filepath': os.path.join(upload_folder, filename)
        }
        try:
            database.write_entry(id_info, FILE_PATH_TABLE)
        except:
            database.create_table(FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA)
            database.write_entry(id_info, FILE_PATH_TABLE)
        
        # TODO: store to GCP bucket
        # blob = bucket.blob(uploaded_file.filename)
        # print('uploading to GCP')
        # blob.upload_from_filename(os.path.join(upload_folder, filename))
        # os.remove(os.path.join(upload_folder, filename))

        # Add IMDB Info
        if ingestor is not None:
            ingestor.ingest(internal_id, uploaded_file.filename)
    
    return '1'

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
