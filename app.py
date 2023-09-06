from flask import Flask, render_template, request, redirect
import base64 
import glob 
import json 
import numpy as np 
from fuzzywuzzy import fuzz 
import numpy as np 
import redis 
import time 

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/player')

@app.route('/player')
def player():
    return '<h1>Test Flask Dockerization</h1>'

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
