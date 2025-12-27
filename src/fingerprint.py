import librosa
import numpy as np
import hashlib
from scipy.ndimage import maximum_filter
from scipy.ndimage import generate_binary_structure, iterate_structure

class AudioFingerprinter:
    """
    Generate audio fingerprints using spectrogram peak detection.
    """
    
    def __init__(self, sample_rate=22050):
        """
        Initialize the fingerprinter.
        
        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
        
        # Spectrogram parameters
        self.n_fft = 2048  # FFT window size
        self.hop_length = 512  # Hop between frames
        
        # Peak finding parameters
        self.min_amplitude = 10  # Minimum peak amplitude
        self.peak_neighborhood_size = 20  # Size of peak detection area
        
        # Fingerprint parameters
        self.fan_value = 5  # Number of peaks to pair with each peak
        self.time_window = 200  # Maximum time difference for peak pairs
        
    def load_audio(self, file_path):
        """
        Load and preprocess audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            y: Audio time series
            sr: Sample rate
        """
        print(f"Loading: {file_path}")
        y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
        return y, sr
    
    def generate_spectrogram(self, y):
        """
        Generate spectrogram from audio.
        
        Args:
            y: Audio time series
            
        Returns:
            spectrogram: 2D array of frequency magnitudes over time
        """
        # Compute Short-Time Fourier Transform
        stft = librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length)
        
        # Convert to magnitude
        spectrogram = np.abs(stft)
        
        return spectrogram
    
    def find_peaks(self, spectrogram):
        """
        Find peaks in the spectrogram using local maximum filter.
        
        Args:
            spectrogram: 2D frequency-time array
            
        Returns:
            peaks: List of (time_idx, freq_idx) tuples
        """
        # Create a structure for peak detection
        struct = generate_binary_structure(2, 1)
        neighborhood = iterate_structure(struct, self.peak_neighborhood_size)
        
        # Find local maxima
        local_max = maximum_filter(spectrogram, footprint=neighborhood) == spectrogram
        
        # Apply amplitude threshold
        background = (spectrogram == 0)
        eroded_background = maximum_filter(background, footprint=neighborhood, mode='constant')
        
        # Boolean mask of peaks (local maxima above threshold)
        detected_peaks = local_max != eroded_background
        
        # Extract peak coordinates
        amps = spectrogram[detected_peaks]
        peaks = np.array(np.where(detected_peaks)).T
        
        # Filter by amplitude
        peaks = peaks[amps > self.min_amplitude]
        
        print(f"Found {len(peaks)} peaks")
        
        return peaks
    
    def generate_hashes(self, peaks):
        """
        Generate hashes from peak pairs.
        
        Args:
            peaks: Array of (freq_idx, time_idx) peak coordinates
            
        Returns:
            fingerprints: List of (hash, time_offset) tuples
        """
        # Sort peaks by time
        peaks = peaks[peaks[:, 1].argsort()]
        
        fingerprints = []
        
        for i in range(len(peaks)):
            freq1, time1 = peaks[i]
            
            # Look ahead in time for pairing peaks
            for j in range(i + 1, min(i + self.fan_value, len(peaks))):
                freq2, time2 = peaks[j]
                
                # Check if within time window
                time_delta = time2 - time1
                if time_delta > self.time_window:
                    break
                
                # Create hash from frequency pair and time delta
                hash_string = f"{freq1}|{freq2}|{time_delta}"
                hash_value = hashlib.sha1(hash_string.encode('utf-8')).hexdigest()
                
                # Store hash with anchor time
                fingerprints.append((hash_value, int(time1)))
        
        print(f"Generated {len(fingerprints)} fingerprints")
        
        return fingerprints
    
    def fingerprint_file(self, file_path):
        """
        Generate fingerprints for an entire audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            fingerprints: List of (hash, time_offset) tuples
        """
        # Load audio
        y, sr = self.load_audio(file_path)
        
        # Generate spectrogram
        spectrogram = self.generate_spectrogram(y)
        
        # Find peaks
        peaks = self.find_peaks(spectrogram)
        
        # Generate hashes
        fingerprints = self.generate_hashes(peaks)
        
        return fingerprints

if __name__ == "__main__":
    # Test on one file
    fingerprinter = AudioFingerprinter()
    fingerprints = fingerprinter.fingerprint_file("data/movies/the_dictator.mp3")
    
    print(f"\n✅ Generated {len(fingerprints)} fingerprints")
    print(f"Sample fingerprints:")
    for i in range(min(5, len(fingerprints))):
        hash_val, time_offset = fingerprints[i]
        print(f"  Hash: {hash_val[:16]}... | Time: {time_offset}")