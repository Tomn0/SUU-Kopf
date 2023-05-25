from flask import Flask, request, jsonify
import time
from enum import IntEnum

app = Flask(__name__)

@app.route('/', methods=['GET'])
def test():
    return jsonify({'text': 'Hello world!'}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
