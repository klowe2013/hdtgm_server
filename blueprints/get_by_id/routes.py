from flask import Blueprint, current_app, Response, send_file, render_template, request 
from python.constants import FILE_PATH_TABLE, EPISODE_INFO
from python.EpisodeCard import EpisodeCard
import json 
import time 
import base64 
from io import BytesIO

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

@id_bp.route('/stream_by_id/<string:id>')
def audio_stream(id):
    # Get path to file
    this_file = database.query(
        f"""
        select FILEPATH from {FILE_PATH_TABLE} 
        where id=='{id}'
        """
    )['FILEPATH'].values[0]

    print(f'Streaming "{this_file}" from GCP')
    def generate():
        with open(this_file, 'rb') as f:
            data = f.read(1024)
            n_reads = 0
            while data:
                yield data 
                data = f.read(1024 * (2**n_reads))
                n_reads += 1 
    return Response(generate(), mimetype='audio/mp3')
    
@id_bp.route('/audio_by_id/<string:id>_<int:chunk>')
def get_audio_by_id(id, chunk):

    print(f'pulling audio for id {id}, chunk {chunk}')
    # Default to pull from Redis cache
    start_time = time.time()
    
    # Get path to file
    this_file = database.query(
        f"""
        select FILEPATH from {FILE_PATH_TABLE} 
        where id=='{id}'
        """
    )['FILEPATH'].values[0]

    with open(this_file, 'rb') as f:
        f.seek(int(2e6*chunk))
        audio_data = base64.b64encode(f.read(int(2e6))).decode('UTF-8')
        print(f'Loaded data from source file in {time.time()-start_time:.2f}s: {audio_data[:100]}')
        
    data = {"snd": audio_data}
    res = app.response_class(response=json.dumps(data),
        status=200,
        mimetype='application/json')
    return res

@id_bp.route('/episode_cards/<string:id>')
def get_episode_card(id):
    
    data = EpisodeCard(id, database=database).get_card_info()
    
    return render_template('episode_info.html', **data)
