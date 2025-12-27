from pathlib import Path
from fingerprint import AudioFingerprinter
from database import FingerprintDatabase
import re

def parse_filename(file_path):
    """
    Extract metadata from filename and path.
    
    Args:
        file_path: Path object to audio file
        
    Returns:
        Dictionary with title, type, season, episode
    """
    file_name = file_path.stem  # Filename without extension
    parent_folder = file_path.parent.name
    grandparent_folder = file_path.parent.parent.name
    
    # Check if it's a TV show (in tv_shows folder)
    if grandparent_folder == "tv_shows":
        # Extract season/episode if in filename (e.g., s01e01, S05E14)
        match = re.search(r's(\d+)e(\d+)', file_name, re.IGNORECASE)
        
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            # Remove season/episode from title
            title = re.sub(r's\d+e\d+', '', file_name, flags=re.IGNORECASE).strip('_ -')
        else:
            season = None
            episode = None
            title = file_name
        
        # Use parent folder as show name if title is generic
        if not title or len(title) < 3:
            title = parent_folder.replace('_', ' ').title()
        
        return {
            'title': title,
            'type': 'tv',
            'season': season,
            'episode': episode,
            'show_name': parent_folder.replace('_', ' ').title()
        }
    else:
        # It's a movie
        return {
            'title': file_name.replace('_', ' ').title(),
            'type': 'movie',
            'season': None,
            'episode': None,
            'show_name': None
        }

def build_database(data_dir="data"):
    """
    Build the fingerprint database from all audio files.
    
    Args:
        data_dir: Root directory containing audio files
    """
    print("="*70)
    print("🎵 BUILDING FINGERPRINT DATABASE")
    print("="*70)
    
    # Initialize components
    fingerprinter = AudioFingerprinter()
    db = FingerprintDatabase()
    
    # Find all audio files
    data_path = Path(data_dir)
    audio_files = list(data_path.rglob("*.mp3"))
    
    print(f"\n📁 Found {len(audio_files)} audio files")
    print("="*70)
    
    # Process each file
    for idx, audio_file in enumerate(audio_files, 1):
        print(f"\n[{idx}/{len(audio_files)}] Processing: {audio_file.name}")
        print("-"*70)
        
        try:
            # Parse metadata from filename
            metadata = parse_filename(audio_file)
            
            # Display metadata
            if metadata['type'] == 'tv':
                display_title = f"{metadata['show_name']}"
                if metadata['season'] and metadata['episode']:
                    display_title += f" - S{metadata['season']:02d}E{metadata['episode']:02d}"
                print(f"📺 TV Show: {display_title}")
            else:
                print(f"🎬 Movie: {metadata['title']}")
            
            # Generate fingerprints
            fingerprints = fingerprinter.fingerprint_file(str(audio_file))
            
            # Add to database
            media_id = db.add_media(
                title=metadata['title'],
                media_type=metadata['type'],
                file_path=str(audio_file),
                season=metadata['season'],
                episode=metadata['episode']
            )
            
            db.add_fingerprints(media_id, fingerprints)
            
            print(f"✅ Successfully processed!")
            
        except Exception as e:
            print(f"❌ Error processing {audio_file.name}: {e}")
            continue
    
    # Display final statistics
    print("\n" + "="*70)
    print("📊 FINAL DATABASE STATISTICS")
    print("="*70)
    
    stats = db.get_statistics()
    print(f"Total Media Items: {stats['total_media']}")
    print(f"  - Movies: {stats['movies']}")
    print(f"  - TV Shows: {stats['tv_shows']}")
    print(f"Total Fingerprints: {stats['total_fingerprints']:,}")
    
    # Show all media
    print("\n📋 Media Library:")
    print("-"*70)
    all_media = db.get_all_media()
    
    for media in all_media:
        if media['type'] == 'tv':
            if media['season'] and media['episode']:
                print(f"  📺 {media['title']} - S{media['season']:02d}E{media['episode']:02d} "
                      f"({media['fingerprint_count']:,} fingerprints)")
            else:
                print(f"  📺 {media['title']} ({media['fingerprint_count']:,} fingerprints)")
        else:
            print(f"  🎬 {media['title']} ({media['fingerprint_count']:,} fingerprints)")
    
    db.close()
    
    print("\n" + "="*70)
    print("✅ Database build complete!")
    print("="*70)

if __name__ == "__main__":
    build_database()