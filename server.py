#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
import re
from pathlib import Path

PORT = 80

# Try to import mutagen for metadata extraction
try:
    from mutagen import File
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("Warning: mutagen library not found. Install with: pip install mutagen")
    print("Song metadata (title, artist) will not be available without it.")

class MusicPlayerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        if self.path == '/playlist':
            self.send_playlist()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/reorder':
            self.reorder_playlist()
        else:
            self.send_error(404)
    
    def extract_metadata(self, filepath):
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
                    # TPE1 is the main contributing artist field
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
    
    def send_playlist(self):
        playlist_dir = Path(__file__).parent / 'playlist'
        files = []
        
        if playlist_dir.exists():
            # Get all files and sort them (respecting numeric prefixes)
            all_files = []
            for file in playlist_dir.iterdir():
                if file.is_file():
                    all_files.append(file)
            
            # Sort files: first by numeric prefix, then by name
            def sort_key(f):
                # Check if filename starts with a number
                match = re.match(r'^(\d+)[._-]', f.name)
                if match:
                    return (0, int(match.group(1)), f.name)
                return (1, 0, f.name)
            
            all_files.sort(key=sort_key)
            
            for file in all_files:
                # Remove numeric prefix for display
                display_name = re.sub(r'^\d+[._-]', '', file.name)
                
                # Extract metadata
                title, artist = self.extract_metadata(file)
                
                files.append({
                    'filename': file.name,
                    'title': title,
                    'artist': artist
                })
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(files).encode())
    
    def reorder_playlist(self):
        """Reorder files in the playlist folder by adding numeric prefixes"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            files = data.get('files', [])
            if not files:
                self.send_error(400, "No files provided")
                return
            
            playlist_dir = Path(__file__).parent / 'playlist'
            if not playlist_dir.exists():
                self.send_error(404, "Playlist directory not found")
                return
            
            # Create a mapping of current filenames to their paths
            file_map = {}
            for file in playlist_dir.iterdir():
                if file.is_file():
                    # Remove any existing numeric prefix for matching
                    clean_name = re.sub(r'^\d+[._-]', '', file.name)
                    file_map[clean_name] = file
            
            # Rename files with new numeric prefixes
            for index, filename in enumerate(files):
                # Remove existing numeric prefix
                clean_name = re.sub(r'^\d+[._-]', '', filename)
                
                if clean_name in file_map:
                    old_path = file_map[clean_name]
                    # Create new filename with numeric prefix
                    new_name = f"{index + 1:03d}_{clean_name}"
                    new_path = playlist_dir / new_name
                    
                    # Only rename if the name is different
                    if old_path != new_path:
                        # If new path already exists, remove it first
                        if new_path.exists():
                            new_path.unlink()
                        old_path.rename(new_path)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MusicPlayerHandler) as httpd:
        print(f"Music Player running at http://localhost:{PORT}")
        print(f"Place your MP3/MP4 files in the 'playlist' folder")
        if MUTAGEN_AVAILABLE:
            print("Metadata extraction enabled")
        else:
            print("Install mutagen for metadata: pip install mutagen")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            httpd.server_close()
