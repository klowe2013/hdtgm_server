from flask import Blueprint, render_template, current_app
from python.constants import EPISODE_INFO 

app = current_app
with app.app_context():
    database = current_app.config['database']
    player_bp = Blueprint(
        'player_bp', __name__, template_folder='templates', static_folder='static'
    )

@player_bp.route('/player')
def player():
    all_titles = [
        str(v) 
        for v in database.query(f'select distinct(imdb_title) from {EPISODE_INFO}')['IMDB_TITLE'].values
    ]
    template_data = {
        'title': 'HDTGM Episode Player',
        'episodes': {ie: episode for ie, episode in enumerate(all_titles)}
    }
    return render_template('player.html', **template_data)

