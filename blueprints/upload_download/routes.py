from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
<<<<<<< HEAD
from python.constants import FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA, GCLOUD_PREFIX
from python.EpisodeIngestor import EpisodeIngestor 
import uuid 
import os 
from google.cloud import storage

client = storage.Client('hdtgm-player')
bucket = client.get_bucket('hdtgm-episodes')
=======
from python.constants import FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA, MEDIA_FOLDER
from python.EpisodeIngestor import EpisodeIngestor 
import uuid 
import os 
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("upload_routes")
>>>>>>> staging

app = current_app
with app.app_context():
    database = current_app.config['database']
    upload_bp = Blueprint(
        'upload_bp', __name__, static_folder='static'
    )

@upload_bp.route('/episode_upload', methods=['GET', 'POST'])
def episode_upload():
    ingestor = EpisodeIngestor()
    logging.info(request.files)
    uploaded_files = request.files.getlist('file')
    logging.info(f'received {uploaded_files}')
    for uploaded_file in uploaded_files:
<<<<<<< HEAD
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(upload_folder, filename))
=======
        uploaded_file.save(os.path.join(MEDIA_FOLDER, uploaded_file.filename))
>>>>>>> staging

        # Get title, episode number, ID
        internal_id = str(uuid.uuid4())
        # Open blob on GCP
        print('Opening blob')
        blob = bucket.blob(os.path.join(GCLOUD_PREFIX, uploaded_file.filename))
        # Upload the file
        print(f'Uploading {filename} to blob')
        blob.upload_from_filename(os.path.join(upload_folder, filename))
        # Remove from local
        print('cleaning locally')
        os.remove(os.path.join(upload_folder, filename))
        
        id_info = {
            'id': internal_id,
<<<<<<< HEAD
            'filepath': os.path.join(GCLOUD_PREFIX, uploaded_file.filename)
=======
            'filepath': os.path.join(MEDIA_FOLDER, uploaded_file.filename)
>>>>>>> staging
        }

        print(f'Entering path info {id_info} to DB')
        try:
            database.write_entry(id_info, FILE_PATH_TABLE)
        except:
            database.create_table(FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA)
            database.write_entry(id_info, FILE_PATH_TABLE)
        
        # Add IMDB Info
        if ingestor is not None:
            ingestor.ingest(internal_id, uploaded_file.filename)
    
    return '1'
