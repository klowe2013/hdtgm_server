from flask import Flask, render_template, request, redirect
import base64 
import glob 
import json 
import numpy as np 
from fuzzywuzzy import fuzz 
import numpy as np 

app = Flask(__name__)

BASE_DIR = '/Users/kaleb/Documents/HDTGM Episodes/'

all_files = glob.glob(f'{BASE_DIR}/*')
all_filenames = sorted([f.split('/')[-1] for f in all_files])
all_titles = [f.replace('_', '') for f in all_filenames]
    
@app.route('/')
def index():
    return redirect('/player')

@app.route('/player')
def player():
    template_data = {
        'title': 'HDTGM Episode Player',
        'n_episodes': len(all_files),
        'episodes': {ie: episode for ie, episode in enumerate(all_titles)}
    }
    return render_template('player.html', **template_data)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    template_data = {
        'title': 'HDTGM Episode Lookup',
        'n_episodes': len(all_files),
        'episodes': {}
    }
    return render_template('search_page.html', **template_data)

@app.route('/search_text', methods=['GET', 'POST'])
def search_text():
    # Check for params
    try:
        request_params = request.get_json()
    except:
        request_params = {}

    search_text = request_params.get('search_text', '')
    n_results = int(request_params.get('n_results', '5'))

    fuzzy_match_ratios = np.array([fuzz.partial_ratio(search_text, f) for f in all_titles])
    match_inds = np.argsort(fuzzy_match_ratios)[::-1]
    search_data = {
        'episodes': {int(match): all_titles[match] for match in match_inds[:n_results]}
    }
    
    res = app.response_class(response=json.dumps(search_data),
        status=200,
        mimetype='application/json')
    return res


@app.route('/audio_by_id/<int:id>')
def get_audio_by_id(id):
    
    print(f'pulling audio for id {id}')

    with open(f"{BASE_DIR}/{all_filenames[id]}", 'rb') as f:
        audio_data = base64.b64encode(f.read()).decode('UTF-8')

    data = {"snd": audio_data}
    res = app.response_class(response=json.dumps(data),
        status=200,
        mimetype='application/json')
    return res

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
