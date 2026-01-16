# 🎵 Audio Recognition System

A proof-of-concept media recognition system that identifies movies and TV shows from short audio clips using audio fingerprinting technology - similar to how Shazam identifies music.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

##  Project Overview

This system uses **audio fingerprinting** to identify media content from 5-10 second audio clips. It demonstrates:

- Digital signal processing with spectrograms
- Peak detection and feature extraction
- Combinatorial hashing algorithms
- Time-alignment matching
- Full-stack web development

##  Features

- **Audio Fingerprinting Engine**: Generates unique fingerprints from audio using spectrogram analysis
- **Fast Matching Algorithm**: Identifies content using time-offset alignment scoring
- **Web Interface**: Modern, responsive UI for uploading and identifying audio clips
- **CLI Tool**: Command-line interface for batch processing and testing
- **SQLite Database**: Efficient storage and retrieval of 50,000+ fingerprints

##  Tech Stack

- **Backend**: Python 3.11, Flask
- **Audio Processing**: librosa, numpy, scipy
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Glassmorphism, gradient effects, responsive layout

##  How It Works

### 1. Fingerprint Generation
```
Audio File → STFT → Spectrogram → Peak Detection → Hash Generation → Database
```

- Converts audio to frequency-time representation (spectrogram)
- Identifies prominent frequency peaks (constellation points)
- Creates combinatorial hashes from peak pairs
- Stores hashes with timestamp metadata

### 2. Matching Algorithm
```
Query Clip → Generate Fingerprints → Search Database → Score Matches → Return Best Match
```

- Generates fingerprints from unknown clip
- Searches for matching hashes in database
- Uses time-offset alignment to score candidates
- Returns match with highest confidence score

##  Project Structure
```
media-recognition/
├── src/
│   ├── fingerprint.py      # Audio fingerprinting engine
│   ├── database.py          # Database operations
│   ├── matcher.py           # Matching algorithm
│   ├── app.py               # Flask web server
│   ├── audio_inspector.py   # Dataset validation tool
│   └── build_database.py    # Database population script
├── frontend/
│   └── templates/
│       └── index.html       # Web interface
├── data/
│   ├── movies/              # Movie audio files (not in repo)
│   ├── tv_shows/            # TV show audio files (not in repo)
│   └── test_clips/          # Test clips (not in repo)
├── database/
│   └── fingerprints.db      # SQLite database (not in repo)
├── requirements.txt
└── README.md
```

## 🔧 Installation

### Prerequisites
- Python 3.11+
- macOS (or Linux/Windows with minor modifications)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Awwal-10/media-recognition.git
cd media-recognition
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add your audio files**
- Place movie audio files in `data/movies/`
- Place TV show audio files in `data/tv_shows/SHOW_NAME/`
- Supported formats: MP3, WAV, M4A

5. **Build the database**
```bash
python src/build_database.py
```

## 💻 Usage

### Web Interface

1. **Start the server**
```bash
python src/app.py
```

2. **Open browser**
```
http://localhost:5001
```

3. **Upload a clip and identify!**

### Command Line Interface
```bash
python src/matcher.py data/test_clips/your_clip.mp3
```

##  Performance

- **Database Size**: 50,000+ fingerprints from 12 media items
- **Match Accuracy**: ~67% on test set (4/6 successful identifications)
- **Query Time**: 5-10 seconds per clip
- **Best Results**: Music-heavy or action sequences
- **Limitations**: Struggles with pure dialogue scenes

##  Learning Outcomes

This project demonstrates understanding of:

- **Digital Signal Processing**: STFT, spectrograms, frequency analysis
- **Algorithm Design**: Peak detection, hashing, time-alignment scoring
- **Database Design**: Schema optimization, indexing, efficient queries
- **Full-Stack Development**: Backend APIs, frontend UI, system integration
- **Software Engineering**: Modular code, documentation, version control

##  Limitations & Future Improvements

### Current Limitations
- Works best with music/action audio, struggles with pure dialogue
- Limited to local dataset (not production-scale)
- No real-time microphone recording
- Basic UI (functional proof-of-concept)

### Potential Improvements
- [ ] Add microphone recording capability
- [ ] Implement real-time streaming analysis
- [ ] Optimize fingerprint algorithm for dialogue
- [ ] Add confidence thresholds and quality metrics
- [ ] Deploy to cloud with larger dataset
- [ ] Add user authentication and history tracking

##  Note on Copyright

This is an **educational proof-of-concept project**. Audio files are **not included** in this repository. Users must provide their own legally obtained audio for testing purposes. The system generates transformative fingerprints for identification purposes only and does not distribute copyrighted content.

##  License

MIT License - feel free to use this code for learning purposes.

## 👤 Author

**Your Name**
- GitHub: [Awwal-Github](https://github.com/Awwal-10)
- LinkedIn: [Awwal-LinkedIn](https://www.linkedin.com/in/awwal-ahmed10/)
- Portfolio: [Awwal-Portfolio](https://bit.ly/AwwalStudentPage)

##  Acknowledgments

- Audio processing powered by [librosa](https://librosa.org/)
- Inspired by the Shazam audio fingerprinting algorithm
- Built as a portfolio project to demonstrate full-stack engineering skills

---

**⭐ If you found this project interesting, please consider starring it!**
