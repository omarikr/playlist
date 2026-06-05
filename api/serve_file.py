import os
from pathlib import Path

def handler(request):
    """Serve individual files from the playlist directory with range request support"""
    # Get the filename from the URL path
    path_parts = request.path.split('/')
    filename = path_parts[-1] if path_parts else ''
    
    # Remove query parameters if present
    if '?' in filename:
        filename = filename.split('?')[0]
    
    playlist_dir = Path(__file__).parent.parent / 'playlist'
    file_path = playlist_dir / filename
    
    print(f"Serving file: {file_path}, exists: {file_path.exists()}")
    
    if not file_path.exists() or not file_path.is_file():
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'text/plain'
            },
            'body': 'File not found'
        }
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Determine content type based on file extensions
    content_type = 'application/octet-stream'
    if filename.endswith('.mp3'):
        content_type = 'audio/mpeg'
    elif filename.endswith('.mp4'):
        content_type = 'audio/mp4'
    elif filename.endswith('.wav'):
        content_type = 'audio/wav'
    elif filename.endswith('.m4a'):
        content_type = 'audio/mp4'
    
    # Handle range requests
    range_header = request.headers.get('range') if hasattr(request, 'headers') else None
    if not range_header and hasattr(request, 'get'):
        range_header = request.get('headers', {}).get('range')
    
    if range_header:
        # Parse range header (e.g., "bytes=0-1023")
        try:
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Validate range
            if start >= file_size or end >= file_size or start > end:
                return {
                    'statusCode': 416,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'text/plain',
                        'Content-Range': f'bytes */{file_size}'
                    },
                    'body': 'Requested range not satisfiable'
                }
            
            # Read the requested range
            with open(file_path, 'rb') as f:
                f.seek(start)
                file_content = f.read(end - start + 1)
            
            return {
                'statusCode': 206,
                'headers': {
                    'Content-Type': content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Accept-Ranges': 'bytes',
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Content-Length': str(len(file_content)),
                    'Cache-Control': 'no-cache'
                },
                'body': file_content,
                'isBase64Encoded': True
            }
        except Exception as e:
            print(f"Error processing range request: {e}")
            # Fall back to full file serve
    
    # Serve full file
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(file_size),
            'Cache-Control': 'no-cache'
        },
        'body': file_content,
        'isBase64Encoded': True
    }

