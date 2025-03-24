"""
Summer AI Assistant - Text-to-Speech Engine
-----------------------------------------
Converts text responses to spoken audio using OpenAI's TTS API.
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class TTSEngine:
    """
    Text-to-Speech engine that converts text responses to spoken audio.
    
    This class uses OpenAI's TTS API to generate natural-sounding speech.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TTS engine with the specified configuration.
        
        Args:
            config: Configuration dictionary for the TTS engine
        """
        self.logger = logging.getLogger("summer.tts")
        self.config = config or {}
        
        # Default configuration
        self.voice = self.config.get("voice", "nova")  # Female voice
        self.model = self.config.get("model", "gpt-4o-mini-tts")
        self.output_format = self.config.get("output_format", "mp3")
        self.instructions = self.config.get("instructions", "Speak in a natural, helpful tone.")
        self.enabled = self.config.get("enabled", True)
        
        # OpenAI API key from config or environment
        self.api_key = self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        
        # Check if OpenAI is available
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not found. TTS will be disabled.")
            self.enabled = False
        
        # Check if VLC is available for audio playback
        if not VLC_AVAILABLE:
            self.logger.warning("VLC library not found. Will use system default player.")
        
        # Initialize OpenAI client if API key is available
        if self.enabled and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            if self.enabled:
                self.logger.warning("OpenAI API key not found. TTS will be disabled.")
                self.enabled = False
            self.client = None
        
        # Create a temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp(prefix="summer_tts_")
        
        # Initialize player
        self.player = None
        if VLC_AVAILABLE:
            self.player = vlc.Instance("--no-video")
        
        self.logger.info(f"TTS Engine initialized with voice: {self.voice}, enabled: {self.enabled}")
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to convert to speech
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            self.logger.warning("TTS is disabled or not configured properly")
            return False
        
        try:
            self.logger.info(f"Converting to speech: '{text}'")
            
            # Generate a unique filename
            timestamp = int(time.time())
            speech_file_path = Path(self.temp_dir) / f"speech_{timestamp}.{self.output_format}"
            
            # Call the OpenAI API to generate speech
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                instructions=self.instructions
            )
            
            # Save to file
            response.stream_to_file(str(speech_file_path))
            
            # Play the audio
            self._play_audio(speech_file_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in TTS: {e}")
            return False
    
    def _play_audio(self, file_path: Path) -> None:
        """
        Play an audio file.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            if VLC_AVAILABLE and self.player:
                # Use VLC for playback
                media = self.player.media_new(str(file_path))
                player = self.player.media_player_new()
                player.set_media(media)
                player.play()
                
                # Wait for playback to complete
                # This is a simple implementation; a more robust one would use events
                time.sleep(0.5)  # Give it time to start
                while player.is_playing():
                    time.sleep(0.1)
            else:
                # Fallback to system default player
                if os.name == 'posix':  # macOS or Linux
                    os.system(f"open {file_path}")
                elif os.name == 'nt':  # Windows
                    os.system(f"start {file_path}")
                
                # Crude estimation of audio length: ~1 second per 15 characters
                estimated_duration = len(str(file_path)) / 15
                time.sleep(estimated_duration)
        
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
    
    def shutdown(self) -> None:
        """Release resources and shutdown the TTS engine."""
        self.logger.info("Shutting down TTS engine")
        
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary files: {e}")