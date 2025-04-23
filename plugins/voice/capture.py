"""
Voice capture and transcription module using OpenAI's Whisper.
"""

import os
import tempfile
import wave
import pyaudio
import whisper
import numpy as np
from typing import Optional, Tuple

class VoiceCapture:
    """Audio capture and transcription using Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the voice capture system.
        
        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large, turbo)
        """
        self.model = whisper.load_model(model_name)
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        
    def record_audio(self, seconds: int = 5) -> np.ndarray:
        """
        Record audio for the specified number of seconds.
        
        Args:
            seconds: Duration to record in seconds
            
        Returns:
            NumPy array of audio data
        """
        print(f"Recording for {seconds} seconds...")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        for _ in range(0, int(self.rate / self.chunk * seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
            
        stream.stop_stream()
        stream.close()
        
        # Convert frames to numpy array
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
        
        return audio_data
    
    def save_audio(self, audio_data: np.ndarray, filename: str) -> None:
        """
        Save recorded audio to a WAV file.
        
        Args:
            audio_data: Audio data as numpy array
            filename: Output filename
        """
        # Convert float32 back to int16
        int_data = (audio_data * 32768).astype(np.int16)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(int_data.tobytes())
    
    def transcribe(self, audio_data: Optional[np.ndarray] = None, 
                  audio_path: Optional[str] = None, 
                  language: Optional[str] = None) -> Tuple[str, float]:
        """
        Transcribe audio using Whisper.
        
        Args:
            audio_data: Audio data (if provided instead of file)
            audio_path: Path to audio file (if provided instead of data)
            language: Optional language hint for Whisper
            
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        if audio_data is not None:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                self.save_audio(audio_data, temp_file.name)
                audio_path = temp_file.name
        
        if not audio_path:
            raise ValueError("Either audio_data or audio_path must be provided")
            
        # Transcribe audio using Whisper
        result = self.model.transcribe(
            audio_path,
            language=language,
            fp16=False  # Use float32 for better compatibility
        )
        
        # Clean up temporary file if we created one
        if audio_data is not None:
            os.unlink(audio_path)
            
        return result["text"], result.get("confidence", 0.0)
        
    def capture_and_transcribe(self, seconds: int = 5, language: Optional[str] = None) -> str:
        """
        Record audio and transcribe in one step.
        
        Args:
            seconds: Duration to record in seconds
            language: Optional language hint
            
        Returns:
            Transcribed text
        """
        audio_data = self.record_audio(seconds)
        text, confidence = self.transcribe(audio_data=audio_data, language=language)
        
        print(f"Transcription confidence: {confidence:.2f}")
        return text
        
    def __del__(self):
        """Clean up PyAudio resources."""
        self.audio.terminate()

if __name__ == "__main__":
    # Test the voice capture and transcription
    capturer = VoiceCapture(model_name="tiny")  # Use the smallest model for testing
    
    print("Starting voice capture test...")
    text = capturer.capture_and_transcribe(5)
    print(f"Transcribed: {text}")