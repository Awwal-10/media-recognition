import librosa
import os
from pathlib import Path

def inspect_audio(file_path):
    """
    Load and display basic information about an audio file.
    """
    print(f"\n{'='*60}")
    print(f"Inspecting: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Load audio file
        y, sr = librosa.load(file_path, sr=None)
        
        # Calculate duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Display info
        print(f"Sample Rate: {sr} Hz")
        print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"Total Samples: {len(y)}")
        print(f"Audio Shape: {y.shape}")
        print("✅ File loaded successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False

def scan_dataset(data_dir):
    """
    Scan all audio files in the dataset.
    """
    data_path = Path(data_dir)
    audio_files = list(data_path.rglob("*.mp3"))
    
    print(f"\n🔍 Found {len(audio_files)} audio files")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for audio_file in audio_files:
        if inspect_audio(str(audio_file)):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Summary:")
    print(f"   ✅ Successfully loaded: {success_count}")
    print(f"   ❌ Failed to load: {fail_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    scan_dataset("data")