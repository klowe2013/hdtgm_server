from flask import Flask, render_template, request, redirect
import redis 
import time 
import os 
from python.db_interfaces.DatabaseFactory import DatabaseFactory
from python.constants import SQLITE_DB

# Set up GCP credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './keys/hdtgm-player-3967c005aeb0.json'

# from constants import REDIS_IP, REDIS_PORT
REDIS_IP, REDIS_PORT = os.getenv('REDIS_IP', '172.17.0.1'), 6379

r = 1 #redis.Redis(host=REDIS_IP, port=REDIS_PORT, decode_responses=True)
try: 
    r.set('up_check', 'up')
except:
    r = 1
app = Flask(__name__)

database = DatabaseFactory(SQLITE_DB).create('sqlite')

app.config['database'] = database 
app.config['redis'] = r 

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
