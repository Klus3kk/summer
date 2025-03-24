"""
Summer AI Assistant - Listener Module
-----------------------------------
Handles speech recognition to convert spoken commands to text.
"""

import logging
import time
from typing import Dict, Any, Optional

# Speech recognition libraries
try:
    import speech_recognition as sr
except ImportError:
    sr = None

class Listener:
    """
    Handles converting speech to text using various speech recognition engines.
    
    This class provides a unified interface to different speech recognition backends.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the listener with the specified configuration.
        
        Args:
            config: Configuration dictionary for the listener
        """
        self.logger = logging.getLogger("summer.listener")
        self.config = config or {}
        
        # Default configuration
        self.engine = self.config.get("engine", "google")
        self.timeout = self.config.get("timeout", 5)
        self.phrase_time_limit = self.config.get("phrase_time_limit", 5)
        self.energy_threshold = self.config.get("energy_threshold", 300)
        
        # Check if speech_recognition is available
        if sr is None:
            self.logger.warning("speech_recognition library not found. Using mock implementation.")
            self.recognizer = None
            self.microphone = None
        else:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.energy_threshold
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise (optional)
            if self.config.get("adjust_for_ambient_noise", True):
                with self.microphone as source:
                    self.logger.info("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    self.logger.info("Ambient noise adjustment complete")
        
        self.logger.info(f"Listener initialized with engine: {self.engine}")
    
    def listen(self) -> Optional[str]:
        """
        Listen for a single command.
        
        Returns:
            The recognized text, or None if recognition failed
        """
        if self.recognizer is None:
            self.logger.warning("Speech recognition not available, using mock implementation")
            # In a real implementation, you would replace this with actual input
            # This is just for development without speech recognition
            return input("Enter command: ")
        
        try:
            with self.microphone as source:
                self.logger.info(f"Listening (timeout: {self.timeout}s)...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                self.logger.info("Audio captured, recognizing...")
                
                # Process with the selected engine
                if self.engine == "google":
                    text = self.recognizer.recognize_google(audio)
                elif self.engine == "sphinx":
                    text = self.recognizer.recognize_sphinx(audio)
                elif self.engine == "whisper":
                    # Requires the whisper library to be installed
                    text = self.recognizer.recognize_whisper(audio)
                else:
                    self.logger.error(f"Unknown speech recognition engine: {self.engine}")
                    return None
                
                self.logger.info(f"Recognized: '{text}'")
                return text
                
        except sr.WaitTimeoutError:
            self.logger.info("Listen timeout, no speech detected")
            return None
        except sr.UnknownValueError:
            self.logger.info("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.exception(f"Error during speech recognition: {e}")
            return None
    
    def shutdown(self):
        """Release resources and shutdown the listener."""
        self.logger.info("Shutting down listener")
        # Nothing specific to clean up in this implementation
        # But this method is part of the component interface