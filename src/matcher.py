from collections import defaultdict
from fingerprint import AudioFingerprinter
from database import FingerprintDatabase

class AudioMatcher:
    """
    Match unknown audio clips against the fingerprint database.
    """
    
    def __init__(self, db_path="database/fingerprints.db"):
        """
        Initialize the matcher.
        
        Args:
            db_path: Path to fingerprint database
        """
        self.fingerprinter = AudioFingerprinter()
        self.db = FingerprintDatabase(db_path)
    
    def match_clip(self, audio_path, min_confidence=5):
        """
        Match an audio clip against the database.
        
        Args:
            audio_path: Path to audio clip to identify
            min_confidence: Minimum number of matching fingerprints
            
        Returns:
            Dictionary with match results or None
        """
        print(f"\n{'='*70}")
        print(f"🔍 ANALYZING AUDIO CLIP")
        print(f"{'='*70}")
        print(f"File: {audio_path}")
        
        # Generate fingerprints from the query clip
        print("\nGenerating fingerprints from clip...")
        query_fingerprints = self.fingerprinter.fingerprint_file(audio_path)
        
        if not query_fingerprints:
            print("❌ No fingerprints generated from clip")
            return None
        
        # Extract just the hashes for searching
        query_hashes = [fp[0] for fp in query_fingerprints]
        
        print(f"Searching database for {len(query_hashes)} fingerprints...")
        
        # Search database
        matches = self.db.search_fingerprints(query_hashes)
        
        if not matches:
            print("❌ No matches found in database")
            return None
        
        print(f"Found {len(matches)} matching fingerprints")
        
        # Score matches by media_id and time offset alignment
        scores = self._score_matches(query_fingerprints, matches)
        
        if not scores:
            print("❌ No confident matches after scoring")
            return None
        
        # Get best match
        best_match = max(scores, key=lambda x: x['score'])
        
        if best_match['score'] < min_confidence:
            print(f"❌ Best match score ({best_match['score']}) below confidence threshold ({min_confidence})")
            return None
        
        # Get media information
        media_info = self.db.get_media_info(best_match['media_id'])
        
        # Calculate timestamp
        time_offset_frames = best_match['time_offset']
        time_offset_seconds = (time_offset_frames * self.fingerprinter.hop_length) / self.fingerprinter.sample_rate
        
        result = {
            'media_id': best_match['media_id'],
            'title': media_info['title'],
            'type': media_info['type'],
            'season': media_info['season'],
            'episode': media_info['episode'],
            'confidence': best_match['score'],
            'time_offset_seconds': time_offset_seconds,
            'time_offset_formatted': self._format_time(time_offset_seconds),
            'total_matches': len(matches)
        }
        
        # Display results
        self._display_results(result)
        
        return result
    
    def _score_matches(self, query_fingerprints, db_matches):
        """
        Score matches using time offset alignment.
        
        Args:
            query_fingerprints: List of (hash, time_offset) from query
            db_matches: List of (media_id, hash, time_offset) from database
            
        Returns:
            List of scored matches
        """
        # Create lookup for query fingerprints
        query_dict = {hash_val: time_offset for hash_val, time_offset in query_fingerprints}
        
        # Group matches by media_id and calculate time deltas
        media_matches = defaultdict(list)
        
        for media_id, hash_val, db_time_offset in db_matches:
            if hash_val in query_dict:
                query_time_offset = query_dict[hash_val]
                time_delta = db_time_offset - query_time_offset
                media_matches[media_id].append(time_delta)
        
        # Score each media by finding the most common time delta
        # (indicates alignment between query and database)
        scores = []
        
        for media_id, time_deltas in media_matches.items():
            # Count occurrences of each time delta
            delta_counts = defaultdict(int)
            for delta in time_deltas:
                # Group deltas within a small window (tolerance for timing variations)
                delta_bucket = round(delta / 10) * 10
                delta_counts[delta_bucket] += 1
            
            # Best score is the most common time delta
            best_delta = max(delta_counts, key=delta_counts.get)
            score = delta_counts[best_delta]
            
            scores.append({
                'media_id': media_id,
                'score': score,
                'time_offset': best_delta,
                'total_deltas': len(time_deltas)
            })
        
        return sorted(scores, key=lambda x: x['score'], reverse=True)
    
    def _format_time(self, seconds):
        """
        Format seconds as MM:SS.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted string
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _display_results(self, result):
        """
        Display match results in a formatted way.
        
        Args:
            result: Match result dictionary
        """
        print(f"\n{'='*70}")
        print("✅ MATCH FOUND!")
        print(f"{'='*70}")
        
        if result['type'] == 'tv':
            if result['season'] and result['episode']:
                print(f"📺 Show: {result['title']}")
                print(f"   Season {result['season']}, Episode {result['episode']}")
            else:
                print(f"📺 Show: {result['title']}")
        else:
            print(f"🎬 Movie: {result['title']}")
        
        print(f"\n⏱️  Timestamp: {result['time_offset_formatted']} ({result['time_offset_seconds']:.1f} seconds)")
        print(f"🎯 Confidence: {result['confidence']} matching fingerprints")
        print(f"📊 Total Matches: {result['total_matches']}")
        print(f"{'='*70}")
    
    def close(self):
        """
        Close database connection.
        """
        self.db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/matcher.py <path_to_audio_clip>")
        print("\nExample: python src/matcher.py data/test_clips/clip1.mp3")
        sys.exit(1)
    
    clip_path = sys.argv[1]
    
    matcher = AudioMatcher()
    result = matcher.match_clip(clip_path)
    matcher.close()
    
    if result:
        print("\n✅ Identification successful!")
    else:
        print("\n❌ Could not identify the audio clip")