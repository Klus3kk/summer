"""
Summer AI Assistant - Basic NLP Engine
------------------------------------
Simple NLP engine for basic intent recognition.
"""

import logging
import re
from typing import Dict, Any, Optional, List

class NLPEngine:
    """
    Basic NLP engine for simple command understanding.
    
    This class provides a simple rule-based approach to understanding
    natural language commands.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the NLP engine with the specified configuration.
        
        Args:
            config: Configuration dictionary for the engine
        """
        self.logger = logging.getLogger("summer.basic_nlp")
        self.config = config or {}
        
        # Define patterns for different intents
        self.patterns = {
            "open_application": [
                r"open\s+(?P<app_name>[a-zA-Z0-9\s]+)",
                r"launch\s+(?P<app_name>[a-zA-Z0-9\s]+)",
                r"start\s+(?P<app_name>[a-zA-Z0-9\s]+)"
            ],
            "close_application": [
                r"close\s+(?P<app_name>[a-zA-Z0-9\s]+)",
                r"exit\s+(?P<app_name>[a-zA-Z0-9\s]+)",
                r"quit\s+(?P<app_name>[a-zA-Z0-9\s]+)"
            ],
            "write_text": [
                r"write\s+(?P<content>.+)(\s+in\s+(?P<app_name>[a-zA-Z0-9\s]+))?",
                r"type\s+(?P<content>.+)(\s+in\s+(?P<app_name>[a-zA-Z0-9\s]+))?"
            ],
            "draw_shape": [
                r"draw\s+(a\s+)?(?P<shape>[a-zA-Z0-9\s]+)(\s+in\s+(?P<app_name>[a-zA-Z0-9\s]+))?",
                r"create\s+(a\s+)?(?P<shape>[a-zA-Z0-9\s]+)(\s+in\s+(?P<app_name>[a-zA-Z0-9\s]+))?"
            ]
        }
        
        self.logger.info("Basic NLP Engine initialized")
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a text command into a structured intent and parameters.
        
        Args:
            text: The text to process
            context: Optional context information for better understanding
        
        Returns:
            A dictionary containing the recognized intent and parameters
        """
        context = context or {}
        self.logger.info(f"Processing text: '{text}'")
        
        # Convert to lowercase for easier matching
        text = text.lower().strip()
        
        # Try to match patterns for each intent
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    # Extract parameters from the match groups
                    parameters = {k: v.strip() for k, v in match.groupdict().items() if v}
                    
                    return {
                        "intent": intent,
                        "parameters": parameters,
                        "confidence": 0.8,  # Fixed confidence for rule-based matching
                        "original_text": text
                    }
        
        # If no pattern matched, return unknown intent
        return {
            "intent": "unknown",
            "parameters": {},
            "confidence": 0.0,
            "original_text": text
        }
    
    def shutdown(self):
        """Release resources and shutdown the engine."""
        self.logger.info("Shutting down basic NLP engine")
        # Nothing specific to clean up