from flask import Flask, request, jsonify
import time
import requests
from enum import IntEnum

app = Flask(__name__)

@app.route('/', methods=['GET'])
def test():
    return jsonify({'text': 'Hello world!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
