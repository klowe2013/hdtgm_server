from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from python.constants import FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA 
from python.EpisodeIngestor import EpisodeIngestor 
import uuid 
import os 

app = current_app
with app.app_context():
    database = current_app.config['database']
    upload_bp = Blueprint(
        'upload_bp', __name__, static_folder='static'
    )

@upload_bp.route('/episode_upload', methods=['GET', 'POST'])
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
