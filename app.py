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

# from constants import REDIS_IP, REDIS_PORT
REDIS_IP, REDIS_PORT = os.getenv('REDIS_IP', '172.17.0.1'), 6379

r = 1 #redis.Redis(host=REDIS_IP, port=REDIS_PORT, decode_responses=True)
try: 
    r.set('up_check', 'up')
except:
    r = 1
app = Flask(__name__)

# BASE_DIR = '/hdtgm-player/media/audio_files/'
# BASE_DIR = '/Users/kaleb/Documents/gitRepos/Projects/Hdtgm_webserver/media/audio_files/'
# BASE_DIR = '/Users/kaleb/Documents/HDTGM Episodes/'
BASE_DIR = '/home/pi/Documents/hdtgm_server/media/audio_files/audio_files/'

all_files = glob.glob(f'{BASE_DIR}/*')
all_filenames = sorted([f.split('/')[-1] for f in all_files])
all_titles = [f.replace('_', '') for f in all_filenames]

# try:
ingestor = EpisodeIngestor()
# except:
#     ingestor = None 
    
@app.route('/')
def index():
    return redirect('/search')

@app.route('/player')
def player():
    template_data = {
        'title': 'HDTGM Episode Player',
        'n_episodes': len(all_files),
        'episodes': {ie: episode for ie, episode in enumerate(all_titles)}
    }
    return render_template('player.html', **template_data)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    template_data = {
        'title': 'HDTGM Episode Lookup',
        'n_episodes': len(all_files),
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

    fuzzy_match_ratios = np.array([fuzz.partial_ratio(search_text, f) for f in all_titles])
    match_inds = np.argsort(fuzzy_match_ratios)[::-1]
    search_data = {
        'episodes': {int(match): all_titles[match] for match in match_inds[:n_results]}
    }
    
    res = app.response_class(response=json.dumps(search_data),
        status=200,
        mimetype='application/json')
    return res


@app.route('/audio_by_id/<int:id>')
def get_audio_by_id(id):
    
    print(f'pulling audio for id {id}')

    # Default to pull from Redis cache
    start_time = time.time()
    if hasattr(r, 'set'):
        # Get audio data, or return None if not in redis
        audio_data = r.get(f'audio_data:{id}')
    else:
        # Default to None for next conditional check
        audio_data = None 

    if audio_data is None:
        with open(f"{BASE_DIR}/{all_filenames[id]}", 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('UTF-8')
            print(f'Loaded data from source file in {time.time()-start_time:.2f}s')
            if hasattr(r, 'set'): r.set(f'audio_data:{id}', audio_data)
    else:
        print(f'Loaded data from cache in {time.time()-start_time:.2f}s')

    data = {"snd": audio_data}
    res = app.response_class(response=json.dumps(data),
        status=200,
        mimetype='application/json')
    return res

@app.route('/episode_upload', methods=['GET', 'POST'])
def episode_upload():
    upload_folder = './media/audio_files'
    uploaded_files = request.files.getlist('file')
    for uploaded_file in uploaded_files:
        print(f'Ingesting {uploaded_file.filename}')
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(upload_folder, filename))
        # TODO: store to GCP bucket
        # TODO: add IMDB info to Cassandra ingestion
        if ingestor is not None:
            ingestor.ingest(filename)
        # with open(os.path.join(upload_folder, filename), 'rb') as f:
        #     audio_data = base64.b64encode(f.read(100)).decode('UTF-8')
        # import uuid 
        # file_data = {
        #     'id': uuid.uuid4(),
        #     'filename': filename,
        #     'data': audio_data
        # }
        # print(file_data)

    
    return '1'

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
