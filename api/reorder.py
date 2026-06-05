import json
import re
from pathlib import Path

def handler(request):
    """Handle playlist reorder requests"""
    # Handle both Vercel request object and custom request object
    if hasattr(request, 'method'):
        method = request.method
        body = request.body
    else:
        # Vercel passes a different structure
        method = request.get('method', 'POST')
        body = request.get('body')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        data = json.loads(body)
        files = data.get('files', [])
        
        if not files:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'error': 'No files provided'})
            }
        
        playlist_dir = Path(__file__).parent.parent / 'playlist'
        if not playlist_dir.exists():
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'error': 'Playlist directory not found'})
            }
        
        # Create a mapping of current filenames to their paths
        file_map = {}
        for file in playlist_dir.iterdir():
            if file.is_file():
                clean_name = re.sub(r'^\d+[._-]', '', file.name)
                file_map[clean_name] = file
        
        # Rename files with new numeric prefixes
        for index, filename in enumerate(files):
            clean_name = re.sub(r'^\d+[._-]', '', filename)
            
            if clean_name in file_map:
                old_path = file_map[clean_name]
                new_name = f"{index + 1:03d}_{clean_name}"
                new_path = playlist_dir / new_name
                
                if old_path != new_path:
                    if new_path.exists():
                        new_path.unlink()
                    old_path.rename(new_path)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'success': True})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'error': str(e)})
        }

