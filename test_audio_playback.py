#!/usr/bin/env python3
"""Test Qt audio playback functionality."""

import sys
import numpy as np
import io
import wave
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QBuffer, QIODevice

class TestAudioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        self.setWindowTitle("Test Audio Playback")
        self.setGeometry(100, 100, 300, 100)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        test_button = QPushButton("Generate and Play Test Tone")
        test_button.clicked.connect(self.play_test_tone)
        layout.addWidget(test_button)
        
    def play_test_tone(self):
        """Generate and play a test tone."""
        print("Generating test tone...")
        
        # Generate a 440Hz sine wave for 1 second
        sample_rate = 16000
        duration = 1.0
        frequency = 440.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)
        audio_samples = (audio_data * 32767).astype(np.int16)
        
        # Create WAV in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_samples.tobytes())
        
        wav_data = wav_buffer.getvalue()
        print(f"Generated {len(wav_data)} bytes of audio data")
        
        # Play using Qt
        buffer = QBuffer()
        buffer.setData(wav_data)
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        
        self.media_player.setSourceDevice(buffer)
        self.media_player.play()
        print("Playing audio...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestAudioApp()
    window.show()
    sys.exit(app.exec())