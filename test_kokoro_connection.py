#!/usr/bin/env python3
"""Test script to verify Kokoro TTS functionality."""

import soundfile as sf
from kokoro import KPipeline


def test_kokoro_tts():
    """Test basic Kokoro TTS functionality."""
    try:
        print("Initializing Kokoro pipeline...")
        pipeline = KPipeline(lang_code='a')  # American English
        
        test_text = "Hello! This is a test of the Kokoro 82M text-to-speech system. It's working great!"
        voice = "af_heart"  # Female voice
        
        print(f"Generating speech with voice '{voice}'...")
        print(f"Text: {test_text}")
        
        generator = pipeline(test_text, voice=voice, speed=1.0)
        
        # Collect audio from generator
        audio_segments = []
        for i, (graphemes, phonemes, audio) in enumerate(generator):
            print(f"Segment {i+1}:")
            print(f"  Graphemes: {graphemes}")
            print(f"  Phonemes: {phonemes}")
            audio_segments.append(audio)
        
        # Combine all audio segments
        import numpy as np
        combined_audio = np.concatenate(audio_segments)
        
        # Save to file
        output_file = "kokoro_test_output.wav"
        sf.write(output_file, combined_audio, 24000)
        print(f"\nAudio saved to: {output_file}")
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_kokoro_tts()