import config_elephant
from ElephantCommon import *

import json
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/status')

def index():
    return jsonify({'currentState': 'S_READY',
                       'currentTrackName': '2104211804.mid',
                       'currentTrackLength' : 50.5})

app.run()