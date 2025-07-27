#!/usr/bin/env python3
"""Test script to verify Riva TTS connection and functionality."""

import riva.client
import numpy as np

def test_riva_connection():
    """Test basic Riva TTS functionality."""
    try:
        print("Connecting to Riva server at localhost:50051...")
        auth = riva.client.Auth(
            uri="localhost:50051",
            use_ssl=False,
            metadata_args=[
                ('grpc.max_receive_message_length', 10 * 1024 * 1024),
                ('grpc.keepalive_time_ms', 10000),
                ('grpc.keepalive_timeout_ms', 5000),
            ]
        )
        
        print("Creating TTS service...")
        tts_service = riva.client.SpeechSynthesisService(auth)
        
        print("Testing TTS synthesis...")
        text = "Hello, this is a test."
        voice_name = "English-US.Female-1"
        
        print(f"Synthesizing: '{text}' with voice '{voice_name}'")
        resp = tts_service.synthesize(
            text=text,
            voice_name=voice_name,
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            sample_rate_hz=16000,
            language_code="en-US"
        )
        
        audio_samples = np.frombuffer(resp.audio, dtype=np.int16)
        print(f"Success! Generated {len(audio_samples)} audio samples")
        print(f"Duration: ~{len(audio_samples) / 16000:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_riva_connection()