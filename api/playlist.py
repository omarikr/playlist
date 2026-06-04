import json
import os
import re
from pathlib import Path
from http.server import SimpleHTTPRequestHandler

# Try to import mutagen for metadata extraction
try:
    from mutagen import File
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

def extract_metadata(filepath):
    """Extract title and artist from audio file"""
    if not MUTAGEN_AVAILABLE:
        return None, None
    
    try:
        audio = File(filepath)
        if audio is None:
            return None, None
        
        title = None
        artist = None
        
        # Try different tag formats
        if hasattr(audio, 'tags'):
            tags = audio.tags
            
            # ID3 tags (MP3) - TIT2 is Title, TPE1 is Contributing Artist
            if tags and hasattr(tags, 'get'):
                title = tags.get('TIT2', [None])[0] if tags.get('TIT2') else None
                artist = tags.get('TPE1', [None])[0] if tags.get('TPE1') else None
            
            # Vorbis comments (OGG, FLAC)
            if not title and hasattr(tags, '__getitem__'):
                title = tags.get('TITLE', [None])[0] if tags.get('TITLE') else None
                artist = tags.get('ARTIST', [None])[0] if tags.get('ARTIST') else None
        
        # MP4 tags - ©nam is Title, ©ART is Artist
        if hasattr(audio, '__getitem__'):
            if not title:
                title = audio.get('\xa9nam', [None])[0] if audio.get('\xa9nam') else None
            if not artist:
                artist = audio.get('\xa9ART', [None])[0] if audio.get('\xa9ART') else None
        
        # Convert to string if needed
        if title and not isinstance(title, str):
            title = str(title)
        if artist and not isinstance(artist, str):
            artist = str(artist)
        
        return title, artist
        
    except (ID3NoHeaderError, Exception) as e:
        return None, None

def handler(request):
    """Handle playlist requests"""
    # Get the playlist directory path
    playlist_dir = Path(__file__).parent.parent / 'playlist'
    files = []
    
    if playlist_dir.exists():
        # Get all files and sort them (respecting numeric prefixes)
        all_files = []
        for file in playlist_dir.iterdir():
            if file.is_file():
                all_files.append(file)
        
        # Sort files: first by numeric prefix, then by name
        def sort_key(f):
            match = re.match(r'^(\d+)[._-]', f.name)
            if match:
                return (0, int(match.group(1)), f.name)
            return (1, 0, f.name)
        
        all_files.sort(key=sort_key)
        
        for file in all_files:
            # Extract metadata
            title, artist = extract_metadata(file)
            
            files.append({
                'filename': file.name,
                'title': title,
                'artist': artist
            })
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(files)
    }
