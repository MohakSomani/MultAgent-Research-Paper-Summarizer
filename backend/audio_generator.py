"""Simple audio generation module with fallbacks for missing dependencies."""
from pathlib import Path
import os
import subprocess
import sys
import platform

def check_espeak():
    """Check if espeak or espeak-ng is installed."""
    try:
        # Try to run espeak --version
        subprocess.run(
            ["espeak", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False
        )
        return True
    except FileNotFoundError:
        try:
            # Try espeak-ng instead
            subprocess.run(
                ["espeak-ng", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=False
            )
            return True
        except FileNotFoundError:
            return False

def install_instructions():
    """Return platform-specific espeak installation instructions."""
    system = platform.system().lower()
    if system == 'linux':
        return "Install espeak with: sudo apt-get install espeak"
    elif system == 'darwin':  # macOS
        return "Install espeak with: brew install espeak"
    elif system == 'windows':
        return "Download and install espeak from http://espeak.sourceforge.net/download.html"
    else:
        return "Please install espeak for your platform"

def generate_audio_file(text, output_path):
    """Generate audio from text using TTS with dependency checks."""
    if not check_espeak():
        instructions = install_instructions()
        error_msg = f"Missing dependency: espeak not found. {instructions}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    
    try:
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        print(f"🎵 Generating audio file at {output_path}")
        
        # Lazy import TTS to avoid errors if it's not needed
        try:
            from TTS.api import TTS
            # Use CPU to avoid GPU-related issues
            tts = TTS(model_name="tts_models/en/ljspeech/vits", gpu=False)
            
            # Clean and limit text to avoid issues
            cleaned_text = text.replace('\n', ' ').strip()
            if len(cleaned_text) > 2000:
                cleaned_text = cleaned_text[:2000] + "..."
                
            print(f"Generating audio for text of length: {len(cleaned_text)}")
            
            # Generate the audio file
            tts.tts_to_file(text=cleaned_text, file_path=output_path)
            
            print(f"✅ Audio generation complete: {output_path}")
            return True
        except ImportError:
            print("❌ TTS library not imported correctly.")
            raise
            
    except Exception as e:
        print(f"❌ Error generating audio: {str(e)}")
        raise e
