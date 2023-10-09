from flask import Blueprint, current_app, Response, send_file, render_template, request 
from python.constants import FILE_PATH_TABLE, EPISODE_INFO
from python.EpisodeCard import EpisodeCard
import json 
import time 
import base64 
from io import BytesIO
from mutagen .mp3 import MP3

app = current_app
with app.app_context():
    database = current_app.config['database']
    id_bp = Blueprint(
        'id_bp', __name__, static_folder='static'
    )

@id_bp.route('/download_by_id/<string:id>')
def download_by_id(id):
    
    print(f'Downloading episode {id}')
    this_file = database.query(
        f"""
        select FILEPATH from {FILE_PATH_TABLE} 
        where id=='{id}'
        """
    )['FILEPATH'].values[0]

    with open(this_file, 'rb') as f:
        send_data = BytesIO(f.read())
        
    return  send_file(send_data, download_name=this_file.split('/')[-1], as_attachment=True)


@id_bp.route('/get_info_by_id/<string:id>')
def get_info_by_id(id):
    
    print(f'pulling info for id {id}')
    episode_info = database.query(
        f"""
        select * from {EPISODE_INFO} 
        where id=='{id}'
        """
    ).to_dict(orient='list')
    
    res = app.response_class(response=json.dumps(episode_info),
        status=200,
        mimetype='application/json')
    return res

@id_bp.route('/get_episode_length/<string:id>')
def get_episode_length(id):
    
    print(f'pulling epiosodelength for id {id}')
    episode_info = database.query(
        f"""
        select * from {EPISODE_INFO} 
        where id=='{id}'
        """
    ).to_dict(orient='list')

    # Get path to file
    this_file_name = database.query(
        f"""
        select FILENAME from {EPISODE_INFO} 
        where id=='{id}'
        """
    )['FILENAME'].values[0]

    # this_file = f"/hdtgm-player/data/media/audio_files/{this_file_name}"
    this_file = f"./data/media/audio_files/{this_file_name}"
    
    file_mutagen = MP3(this_file)
    full_duration = file_mutagen.info.length

    duration_info = {'full_duration': full_duration}
    
    res = app.response_class(response=json.dumps(duration_info),
        status=200,
        mimetype='application/json')
    return res

@id_bp.route('/audio_by_id/<string:id>_<int:chunk>')
def get_audio_by_id(id, chunk):

    print(f'pulling audio for id {id}, chunk {chunk}')
    # Default to pull from Redis cache
    start_time = time.time()
    
    # Get path to file
    this_file_name = database.query(
        f"""
        select FILENAME from {EPISODE_INFO} 
        where id=='{id}'
        """
    )['FILENAME'].values[0]

    this_file = f"./data/media/audio_files/{this_file_name}"
    
    with open(this_file, 'rb') as f:
        f.seek(int(2e6*chunk))
        chunk_read = f.read(int(2e6))
        audio_data = base64.b64encode(chunk_read).decode('UTF-8')
        chunk_len = MP3(BytesIO(chunk_read)).info.length
        print(f'Loaded chunk {chunk} of duration {chunk_len}')
        
    data = {"snd": audio_data, "chunk_len": chunk_len}
    res = app.response_class(response=json.dumps(data),
        status=200,
        mimetype='application/json')
    return res

@id_bp.route('/find_chunk/<string:id>', methods=['GET', 'POST'])
def find_chunk(id):
    # Check for params
    try:
        request_params = request.get_json()
    except:
        request_params = {}

    target_time = request_params.get('target_time', 0)
    
    # Get path to file
    this_file_name = database.query(
        f"""
        select FILENAME from {EPISODE_INFO} 
        where id=='{id}'
        """
    )['FILENAME'].values[0]

    this_file = f"./data/media/audio_files/{this_file_name}"
    
    next_chunk = 1
    curr_len = 0
    cum_len = 0
    while cum_len < target_time:
        with open(this_file, 'rb') as f:
            f.seek(int(2e6*(next_chunk-1)))
            x = MP3(BytesIO(f.read(int(2e6))))
            curr_len = x.info.length
            cum_len += curr_len
            next_chunk += 1
            print(f'on chunk {next_chunk}, cumulative length is {cum_len / 60}')
    print(f"Hit {target_time / 60} minutes with chunk {next_chunk}, length {curr_len / 60}")
    res = app.response_class(response=json.dumps({'search_chunk': next_chunk}),
        status=200,
        mimetype='application/json')
    return res


@id_bp.route('/episode_cards/<string:id>')
def get_episode_card(id):
    
    data = EpisodeCard(id, database=database).get_card_info()
    
    return render_template('episode_info.html', **data)
