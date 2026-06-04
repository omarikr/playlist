import os
from pathlib import Path

def handler(request):
    """Serve individual files from the playlist directory"""
    # Get the filename from the URL path
    path_parts = request.path.split('/')
    filename = path_parts[-1] if path_parts else ''
    
    playlist_dir = Path(__file__).parent.parent / 'playlist'
    file_path = playlist_dir / filename
    
    if not file_path.exists() or not file_path.is_file():
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': 'File not found'
        }
    
    # Determine content type based on file extension
    content_type = 'application/octet-stream'
    if filename.endswith('.mp3'):
        content_type = 'audio/mpeg'
    elif filename.endswith('.mp4'):
        content_type = 'audio/mp4'
    elif filename.endswith('.wav'):
        content_type = 'audio/wav'
    elif filename.endswith('.m4a'):
        content_type = 'audio/mp4'
    
    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*',
            'Accept-Ranges': 'bytes'
        },
        'body': file_content,
        'isBase64Encoded': True
    }

# Vercel entry point - compatible with Vercel Python runtime
def app(request, context=None):
    return handler(request)
