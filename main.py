from flask import Flask, render_template, request, redirect
import base64 
import json 
import numpy as np 
import redis 
import time 
import os 
from python.db_interfaces.DatabaseFactory import DatabaseFactory
from python.constants import SQLITE_DB, EPISODE_INFO, FILE_PATH_TABLE, SQLITE_FILEPATH_SCHEMA

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './keys/hdtgm-player-3967c005aeb0.json'

app = Flask(__name__)

database = DatabaseFactory(SQLITE_DB).create('sqlite')

app.config['database'] = database 

with app.app_context():
    from blueprints.player.routes import player_bp
    from blueprints.search.routes import search_bp 
    from blueprints.upload_download.routes import upload_bp
    from blueprints.get_by_id.routes import id_bp
    app.register_blueprint(player_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(id_bp)
    
@app.route('/')
def index():
    return redirect('/search')

@app.route('/testcard')
def test_dard():
    return render_template('test_card.html')

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    template_data = {
        'title': 'HDTGM Episode Lookup',
        'episodes': {}
    }
    return render_template('search_page.html', **template_data)


if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
