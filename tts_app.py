#!/usr/bin/env python3
"""Text-to-Speech Desktop Application using PyQt6 and Kokoro 82M TTS."""

import sys
import io
import wave
import tempfile
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtCore import QUrl, QBuffer, QIODevice
import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline


class KokoroTTSWorker(QThread):
    """Worker thread for Kokoro TTS operations."""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    audio_ready = pyqtSignal(bytes)
    progress_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.text = ""
        self.voice_name = "af_heart"
        self.lang_code = "a"
        self.speed = 1.0
        self.pipeline = None
        
    def set_parameters(
        self, 
        text: str, 
        voice_name: str,
        lang_code: str,
        speed: float
    ) -> None:
        """Set TTS parameters."""
        self.text = text
        self.voice_name = voice_name
        self.lang_code = lang_code
        self.speed = speed
        
    def run(self) -> None:
        """Run Kokoro TTS in separate thread."""
        try:
            # Initialize pipeline if not already done
            if self.pipeline is None or self.pipeline.lang_code != self.lang_code:
                self.progress_update.emit("Initializing Kokoro pipeline...")
                self.pipeline = KPipeline(lang_code=self.lang_code)
            
            self.progress_update.emit("Generating speech...")
            
            # Generate speech
            generator = self.pipeline(
                self.text, 
                voice=self.voice_name,
                speed=self.speed,
                split_pattern=r'\n+'
            )
            
            # Collect all audio segments
            all_audio = []
            for i, (gs, ps, audio) in enumerate(generator):
                self.progress_update.emit(f"Processing segment {i+1}...")
                all_audio.append(audio)
            
            # Concatenate all audio segments
            if all_audio:
                combined_audio = np.concatenate(all_audio)
                
                # Create WAV file in memory
                wav_buffer = io.BytesIO()
                sf.write(wav_buffer, combined_audio, 24000, format='WAV')
                wav_buffer.seek(0)
                
                self.audio_ready.emit(wav_buffer.read())
                self.finished.emit()
            else:
                self.error.emit("No audio generated")
                
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class KokoroTTSApp(QMainWindow):
    """Main Text-to-Speech Application Window for Kokoro TTS."""
    
    def __init__(self):
        super().__init__()
        self.tts_worker = None
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_buffer = None  # Store buffer reference
        self.init_ui()
        
    def init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Kokoro 82M Text-to-Speech Application")
        self.setGeometry(100, 100, 800, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel("Kokoro 82M Text-to-Speech")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title)
        
        # Text input area
        input_group = QGroupBox("Enter Text")
        input_layout = QVBoxLayout()
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Paste or type your text here...")
        self.text_input.setMinimumHeight(200)
        input_layout.addWidget(self.text_input)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Voice settings
        settings_group = QGroupBox("Voice Settings")
        settings_layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "American English",
            "British English",
            "Spanish",
            "French",
            "Hindi",
            "Italian",
            "Japanese",
            "Brazilian Portuguese",
            "Mandarin Chinese"
        ])
        self.lang_combo.currentIndexChanged.connect(self.update_voices)
        lang_layout.addWidget(self.lang_combo)
        settings_layout.addLayout(lang_layout)
        
        # Voice selection
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.update_voices()  # Populate initial voices
        voice_layout.addWidget(self.voice_combo)
        settings_layout.addLayout(voice_layout)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(50, 200)
        self.speed_spin.setValue(100)
        self.speed_spin.setSuffix("%")
        speed_layout.addWidget(self.speed_spin)
        settings_layout.addLayout(speed_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(0, 100)
        self.volume_spin.setValue(100)
        self.volume_spin.setSuffix("%")
        self.volume_spin.valueChanged.connect(self.update_volume)
        volume_layout.addWidget(self.volume_spin)
        settings_layout.addLayout(volume_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.speak_button = QPushButton("Speak")
        self.speak_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.speak_button.clicked.connect(self.speak_text)
        button_layout.addWidget(self.speak_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_button.clicked.connect(self.stop_speaking)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #006B8A;
            }
        """)
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready to synthesize speech")
        
    def update_voices(self) -> None:
        """Update available voices based on selected language."""
        lang_index = self.lang_combo.currentIndex()
        
        # Map language to code and available voices
        lang_voices = {
            0: ("a", ["af_bella", "af_nicole", "af_sarah", "af_heart", "af_fable", "af_sky", "am_adam", "am_michael"]),  # American English
            1: ("b", ["bf_emma", "bf_isabella", "bm_george", "bm_lewis"]),  # British English
            2: ("e", ["ef_sofia", "em_carlos"]),  # Spanish
            3: ("f", ["ff_camille", "fm_pierre"]),  # French
            4: ("h", ["hf_anjali", "hm_raj"]),  # Hindi
            5: ("i", ["if_giulia", "im_marco"]),  # Italian
            6: ("j", ["jf_yuki", "jm_hiroshi"]),  # Japanese
            7: ("p", ["pf_maria", "pm_pedro"]),  # Brazilian Portuguese
            8: ("z", ["zf_xiaomei", "zm_xiaolong"]),  # Mandarin Chinese
        }
        
        lang_code, voices = lang_voices.get(lang_index, ("a", ["af_heart"]))
        
        self.voice_combo.clear()
        self.voice_combo.addItems(voices)
        self.voice_combo.setCurrentIndex(0)
        
    def get_language_code(self) -> str:
        """Get the language code for the selected language."""
        lang_codes = ["a", "b", "e", "f", "h", "i", "j", "p", "z"]
        return lang_codes[self.lang_combo.currentIndex()]
        
    def update_volume(self, value: int) -> None:
        """Update audio output volume."""
        self.audio_output.setVolume(value / 100.0)
        
    def speak_text(self) -> None:
        """Start speaking the text using Kokoro TTS."""
        text = self.text_input.toPlainText().strip()
        
        if not text:
            self.statusBar().showMessage("Please enter some text to speak")
            return
            
        self.speak_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage("Synthesizing speech...")
        
        # Create and configure worker thread
        self.tts_worker = KokoroTTSWorker()
        voice_name = self.voice_combo.currentText()
        lang_code = self.get_language_code()
        speed = self.speed_spin.value() / 100.0
        
        self.tts_worker.set_parameters(text, voice_name, lang_code, speed)
        self.tts_worker.audio_ready.connect(self.play_audio)
        self.tts_worker.finished.connect(self.on_synthesis_finished)
        self.tts_worker.error.connect(self.on_synthesis_error)
        self.tts_worker.progress_update.connect(self.update_status)
        self.tts_worker.start()
        
    def update_status(self, message: str) -> None:
        """Update status bar with progress messages."""
        self.statusBar().showMessage(message)
        
    def play_audio(self, audio_data: bytes) -> None:
        """Play the synthesized audio."""
        self.statusBar().showMessage("Playing audio...")
        
        # Create QBuffer from audio data and store reference
        self.audio_buffer = QBuffer()
        self.audio_buffer.setData(audio_data)
        self.audio_buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        
        # Set media content and play
        self.media_player.setSourceDevice(self.audio_buffer)
        self.media_player.play()
        
    def stop_speaking(self) -> None:
        """Stop the current speech."""
        self.media_player.stop()
        
        if self.tts_worker and self.tts_worker.isRunning():
            self.tts_worker.terminate()
            self.tts_worker.wait()
            
        self.on_synthesis_finished()
        self.statusBar().showMessage("Speech stopped")
        
    def clear_text(self) -> None:
        """Clear the text input."""
        self.text_input.clear()
        self.statusBar().showMessage("Text cleared")
        
    def on_synthesis_finished(self) -> None:
        """Handle speech synthesis completion."""
        self.speak_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def on_synthesis_error(self, error_msg: str) -> None:
        """Handle synthesis errors."""
        self.speak_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage(f"Error: {error_msg}")
        QMessageBox.critical(self, "TTS Error", error_msg)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = KokoroTTSApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()