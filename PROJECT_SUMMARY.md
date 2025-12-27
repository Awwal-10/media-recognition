# Media Recognition System - Project Summary

## Quick Pitch (30 seconds)
"I built an audio recognition system similar to Shazam, but for movies and TV shows. It uses audio fingerprinting to identify content from 5-10 second clips. The system generates unique fingerprints from spectrograms, stores them in a database, and uses time-alignment algorithms to match unknown clips with 67% accuracy."

## Technical Highlights

### Core Algorithm
- **Spectrogram Analysis**: Converts audio to frequency-time representation using STFT
- **Peak Detection**: Identifies prominent frequencies using local maximum filters
- **Combinatorial Hashing**: Creates SHA-1 hashes from frequency pairs and time deltas
- **Time-Alignment Scoring**: Matches clips by finding consistent time offsets

### Tech Stack
- Python 3.11, Flask, librosa, numpy, scipy
- SQLite with indexed lookups
- Modern web interface with glassmorphism design

### Scale
- 12 media items (6 movies, 6 TV episodes)
- 49,566 fingerprints stored
- ~5-10 second query time
- 67% match accuracy on test set

## Demo Flow

1. **Show the Web Interface**
   - Modern, professional UI
   - Drag-and-drop upload
   - Real-time processing

2. **Upload a Test Clip**
   - Use: `dictator_clip.mp3` or `john_wick_clip.mp3`
   - Show results: movie name, timestamp, confidence

3. **Show the Code**
   - `fingerprint.py`: Explain peak detection
   - `matcher.py`: Explain time-alignment algorithm
   - `database.py`: Explain indexing strategy

4. **Discuss Trade-offs**
   - Why it works well on music/action
   - Why it struggles with dialogue
   - How production systems scale this

## Interview Questions & Answers

**Q: How does audio fingerprinting work?**
A: "I extract spectrograms using STFT, find frequency peaks, create hashes from peak pairs with time deltas, and store them with timestamps. Matching uses time-offset alignment to find the most consistent match."

**Q: Why not use machine learning?**
A: "Audio fingerprinting is deterministic and explainable. It doesn't require training data and works with exact matching. ML would be overkill for this problem and harder to debug."

**Q: How would you scale this?**
A: "Add distributed database with sharding by hash prefix, implement parallel processing for fingerprint generation, use caching for popular queries, and add load balancing for the API."

**Q: What was the biggest challenge?**
A: "Balancing sensitivity vs. specificity in peak detection. Too sensitive creates noise, too strict misses matches. I tuned parameters empirically using test clips."

## Links
- **GitHub**: https://github.com/Awwal-10/media-recognition
- **Live Demo**: (Run locally with `python src/app.py`)
- **CLI Demo**: `python src/matcher.py data/test_clips/dictator_clip.mp3`

## Project Files to Show
1. `src/fingerprint.py` - Core algorithm
2. `src/matcher.py` - Matching logic
3. `frontend/templates/index.html` - UI
4. `README.md` - Documentation