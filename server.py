from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import sys
from pathlib import Path

# Add the api directory to the path
api_dir = Path(__file__).parent / 'api'
sys.path.insert(0, str(api_dir))

# Import the handlers
from playlist import handler as playlist_handler
from reorder import handler as reorder_handler
from serve_file import handler as serve_file_handler

app = Flask(__name__, static_folder='.')
CORS(app)

class VercelRequest:
    """Mock Vercel request object for local development"""
    def __init__(self, method, path, body=None):
        self.method = method
        self.path = path
        self.body = body

@app.route('/playlist', methods=['GET', 'OPTIONS'])
def playlist():
    if request.method == 'OPTIONS':
        return '', 200
    
    vercel_request = VercelRequest('GET', '/playlist')
    response = playlist_handler(vercel_request)
    return Response(response['body'], status=response['statusCode'], headers=response['headers'])

@app.route('/reorder', methods=['POST', 'OPTIONS'])
def reorder():
    if request.method == 'OPTIONS':
        return '', 200
    
    vercel_request = VercelRequest('POST', '/reorder', request.data)
    response = reorder_handler(vercel_request)
    return Response(response['body'], status=response['statusCode'], headers=response['headers'])

@app.route('/playlist/<filename>', methods=['GET'])
def serve_file(filename):
    vercel_request = VercelRequest('GET', f'/playlist/{filename}')
    response = serve_file_handler(vercel_request)
    
    if response['statusCode'] == 200:
        if response.get('isBase64Encoded'):
            import base64
            content = base64.b64decode(response['body'])
            return Response(content, status=response['statusCode'], headers=response['headers'])
        else:
            return Response(response['body'], status=response['statusCode'], headers=response['headers'])
    else:
        return Response(response['body'], status=response['statusCode'], headers=response['headers'])

@app.route('/', methods=['GET'])
def index():
    index_path = Path(__file__).parent / 'index.html'
    return send_file(index_path)

@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve static files like background.webp"""
    file_path = Path(__file__).parent / filename
    if file_path.exists() and file_path.is_file():
        return send_file(file_path)
    return 'File not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
