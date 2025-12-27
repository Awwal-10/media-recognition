import sqlite3
from pathlib import Path

class FingerprintDatabase:
    """
    Manage storage and retrieval of audio fingerprints.
    """
    
    def __init__(self, db_path="database/fingerprints.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """
        Create database tables if they don't exist.
        """
        # Media table (movies and TV shows)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                season INTEGER,
                episode INTEGER,
                file_path TEXT NOT NULL UNIQUE,
                fingerprint_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Fingerprints table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT NOT NULL,
                time_offset INTEGER NOT NULL,
                media_id INTEGER NOT NULL,
                FOREIGN KEY (media_id) REFERENCES media(id)
            )
        """)
        
        # Create index for fast hash lookups
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hash 
            ON fingerprints(hash)
        """)
        
        self.conn.commit()
        print("✅ Database tables created/verified")
    
    def add_media(self, title, media_type, file_path, season=None, episode=None):
        """
        Add a media item to the database.
        
        Args:
            title: Media title
            media_type: 'movie' or 'tv'
            file_path: Path to audio file
            season: Season number (for TV shows)
            episode: Episode number (for TV shows)
            
        Returns:
            media_id: ID of the inserted media
        """
        try:
            self.cursor.execute("""
                INSERT INTO media (title, type, season, episode, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (title, media_type, season, episode, file_path))
            
            self.conn.commit()
            media_id = self.cursor.lastrowid
            
            print(f"✅ Added media: {title} (ID: {media_id})")
            return media_id
            
        except sqlite3.IntegrityError:
            # Media already exists, get its ID
            self.cursor.execute("""
                SELECT id FROM media WHERE file_path = ?
            """, (file_path,))
            
            media_id = self.cursor.fetchone()[0]
            print(f"ℹ️  Media already exists: {title} (ID: {media_id})")
            return media_id
    
    def add_fingerprints(self, media_id, fingerprints):
        """
        Add fingerprints for a media item.
        
        Args:
            media_id: ID of the media item
            fingerprints: List of (hash, time_offset) tuples
        """
        # Prepare data for batch insert
        data = [(hash_val, time_offset, media_id) 
                for hash_val, time_offset in fingerprints]
        
        # Batch insert
        self.cursor.executemany("""
            INSERT INTO fingerprints (hash, time_offset, media_id)
            VALUES (?, ?, ?)
        """, data)
        
        # Update fingerprint count
        self.cursor.execute("""
            UPDATE media 
            SET fingerprint_count = ?
            WHERE id = ?
        """, (len(fingerprints), media_id))
        
        self.conn.commit()
        
        print(f"✅ Added {len(fingerprints)} fingerprints for media ID {media_id}")
    
    def search_fingerprints(self, query_hashes):
        """
        Search for matching fingerprints.
        
        Args:
            query_hashes: List of hash strings to search for
            
        Returns:
            matches: List of (media_id, hash, time_offset) tuples
        """
        placeholders = ','.join('?' * len(query_hashes))
        
        self.cursor.execute(f"""
            SELECT media_id, hash, time_offset
            FROM fingerprints
            WHERE hash IN ({placeholders})
        """, query_hashes)
        
        return self.cursor.fetchall()
    
    def get_media_info(self, media_id):
        """
        Get information about a media item.
        
        Args:
            media_id: ID of the media item
            
        Returns:
            Dictionary with media information
        """
        self.cursor.execute("""
            SELECT id, title, type, season, episode, file_path, fingerprint_count
            FROM media
            WHERE id = ?
        """, (media_id,))
        
        row = self.cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'type': row[2],
                'season': row[3],
                'episode': row[4],
                'file_path': row[5],
                'fingerprint_count': row[6]
            }
        return None
    
    def get_all_media(self):
        """
        Get all media items from the database.
        
        Returns:
            List of media dictionaries
        """
        self.cursor.execute("""
            SELECT id, title, type, season, episode, file_path, fingerprint_count
            FROM media
            ORDER BY type, title
        """)
        
        media_list = []
        for row in self.cursor.fetchall():
            media_list.append({
                'id': row[0],
                'title': row[1],
                'type': row[2],
                'season': row[3],
                'episode': row[4],
                'file_path': row[5],
                'fingerprint_count': row[6]
            })
        
        return media_list
    
    def get_statistics(self):
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        # Count total media
        self.cursor.execute("SELECT COUNT(*) FROM media")
        total_media = self.cursor.fetchone()[0]
        
        # Count total fingerprints
        self.cursor.execute("SELECT COUNT(*) FROM fingerprints")
        total_fingerprints = self.cursor.fetchone()[0]
        
        # Count by type
        self.cursor.execute("""
            SELECT type, COUNT(*) 
            FROM media 
            GROUP BY type
        """)
        by_type = dict(self.cursor.fetchall())
        
        return {
            'total_media': total_media,
            'total_fingerprints': total_fingerprints,
            'movies': by_type.get('movie', 0),
            'tv_shows': by_type.get('tv', 0)
        }
    
    def close(self):
        """
        Close database connection.
        """
        self.conn.close()

if __name__ == "__main__":
    # Test database creation
    db = FingerprintDatabase()
    
    # Test adding a media item
    media_id = db.add_media(
        title="Test Movie",
        media_type="movie",
        file_path="data/movies/test.mp3"
    )
    
    # Test adding fingerprints
    test_fingerprints = [
        ("abc123", 100),
        ("def456", 200),
        ("ghi789", 300)
    ]
    db.add_fingerprints(media_id, test_fingerprints)
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"   Total Media: {stats['total_media']}")
    print(f"   Total Fingerprints: {stats['total_fingerprints']}")
    print(f"   Movies: {stats['movies']}")
    print(f"   TV Shows: {stats['tv_shows']}")
    
    db.close()