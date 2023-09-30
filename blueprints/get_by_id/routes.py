from flask import Blueprint, current_app, Response, send_file
from python.constants import FILE_PATH_TABLE, EPISODE_INFO, GCLOUD_PREFIX
import json 
import time 
import base64 
from io import BytesIO
from google.cloud import storage

client = storage.Client('hdtgm-player')
bucket = client.get_bucket('hdtgm-episodes')

app = current_app
with app.app_context():
    database = current_app.config['database']
    r = current_app.config['redis']
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
        audio_blob = bucket.blob(this_file)
        with audio_blob.open('rb') as f:
            data = f.read(1024)
            n_reads = 0
            while data:
                yield data 
                data = f.read(1024 * (2**n_reads))
                n_reads += 1 
    return Response(generate(), mimetype='audio/mp3')
    
@id_bp.route('/audio_by_id/<string:id>')
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
        # Get path to file
        this_file = database.query(
            f"""
            select FILEPATH from {FILE_PATH_TABLE} 
            where id=='{id}'
            """
        )['FILEPATH'].values[0]

        # with open(this_file, 'rb') as f:
        #     audio_data = base64.b64encode(f.read()).decode('UTF-8')
        #     print(f'Loaded data from source file in {time.time()-start_time:.2f}s: {audio_data[:100]}')
        #     if hasattr(r, 'set'): r.set(f'audio_data:{id}', audio_data)
        print(f'Reading "{this_file}" from GCP')
        audio_blob = bucket.blob(this_file)
        with audio_blob.open('rb') as f:
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