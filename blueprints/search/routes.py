from flask import Blueprint, request, current_app
from python.constants import EPISODE_INFO 
from fuzzywuzzy import fuzz 
import numpy as np 
import json 

app = current_app
with app.app_context():
    database = current_app.config['database']
    search_bp = Blueprint(
        'search_bp', __name__, static_folder='static'
    )

@search_bp.route('/search_text', methods=['GET', 'POST'])
def search_text():
    # Check for params
    try:
        request_params = request.get_json()
    except:
        request_params = {}

    search_text = request_params.get('search_text', '')
    n_results = int(request_params.get('n_results', '5'))

    try:
        title_pd = database.query(f'select id, imdb_title, episode_no from {EPISODE_INFO}')
    except BaseException as e:
        print(f"Failed to query episode info table: {str(e)}")
        all_titles, all_ids = [], []
    
    if title_pd is None:
        all_titles, all_ids = [], []
    else:
        all_titles, all_ids, all_numbers = title_pd['IMDB_TITLE'].values, title_pd['ID'].values, title_pd['EPISODE_NO'].values
    
    fuzzy_match_ratios = np.array([fuzz.partial_ratio(search_text, f) for f in all_titles])
    match_inds = np.argsort(fuzzy_match_ratios)[::-1]
    search_data = {
        'episodes': {all_ids[match]: f"#{all_numbers[match]}: {all_titles[match]}" for match in match_inds[:n_results]}
    }
    
    res = app.response_class(response=json.dumps(search_data),
        status=200,
        mimetype='application/json')
    return res
