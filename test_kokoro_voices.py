#!/usr/bin/env python3
"""Test script to showcase different Kokoro voices."""

import soundfile as sf
import numpy as np
from kokoro import KPipeline


def test_kokoro_voices():
    """Test different Kokoro voices."""
    
    # Test configurations
    test_configs = [
        ("a", "af_heart", "American English - Female (Heart)"),
        ("a", "am_adam", "American English - Male (Adam)"),
        ("b", "bf_emma", "British English - Female (Emma)"),
        ("b", "bm_george", "British English - Male (George)"),
    ]
    
    test_text = "Hello! This is a demonstration of the Kokoro text-to-speech system."
    
    for lang_code, voice, description in test_configs:
        try:
            print(f"\nTesting: {description}")
            print(f"Language code: {lang_code}, Voice: {voice}")
            
            # Initialize pipeline for the language
            pipeline = KPipeline(lang_code=lang_code)
            
            # Generate speech
            generator = pipeline(test_text, voice=voice, speed=1.0)
            
            # Collect audio
            audio_segments = []
            for _, _, audio in generator:
                audio_segments.append(audio)
            
            # Combine segments
            combined_audio = np.concatenate(audio_segments)
            
            # Save to file
            output_file = f"kokoro_test_{voice}.wav"
            sf.write(output_file, combined_audio, 24000)
            print(f"Audio saved to: {output_file}")
            
        except Exception as e:
            print(f"Error with {description}: {str(e)}")
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_kokoro_voices()