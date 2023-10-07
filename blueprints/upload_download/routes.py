from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from python.constants import FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA
from python.EpisodeIngestor import EpisodeIngestor 
import uuid 
import os 
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("upload_routes")

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
    upload_folder = './media/audio_files'
    uploaded_files = request.files.getlist('file')
    logging.info(f'received {uploaded_files}')
    for uploaded_file in uploaded_files:
        uploaded_file.save(os.path.join(upload_folder, uploaded_file.filename))

        # Get title, episode number, ID
        internal_id = str(uuid.uuid4())
        
        id_info = {
            'id': internal_id,
            'filepath': os.path.join(upload_folder, uploaded_file.filename)
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
