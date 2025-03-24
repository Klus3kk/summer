"""
Summer AI Assistant - Core Assistant Class
-----------------------------------------
The main coordinator for the Summer AI assistant, orchestrating all components.
"""

import logging
import time
from typing import Dict, Any, Optional

from core.listener import Listener
from core.command_processor import CommandProcessor
from core.response_generator import ResponseGenerator
from core.tts_engine import TTSEngine

# Try to import the advanced LangChain NLP engine, fall back to basic if not available
try:
    from core.langchain_nlp_engine import LangChainNLPEngine as NLPEngine
    USING_LANGCHAIN = True
except ImportError:
    from core.nlp_engine import NLPEngine
    USING_LANGCHAIN = False

class Assistant:
    """Main assistant class that coordinates all components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the assistant with its core components.
        
        Args:
            config: Optional configuration dictionary for the assistant
        """
        self.logger = logging.getLogger("summer.assistant")
        self.logger.info("Initializing Summer Assistant")
        
        # Store configuration
        self.config = config or {}
        
        # Initialize components
        self.listener = Listener(self.config.get("listener", {}))
        
        # Initialize NLP engine (LangChain or basic)
        try:
            self.nlp_engine = NLPEngine(self.config.get("nlp", {}))
            self.logger.info(f"Using {'LangChain' if USING_LANGCHAIN else 'Basic'} NLP engine")
        except Exception as e:
            self.logger.error(f"Error initializing NLP engine: {e}")
            self.logger.info("Falling back to basic NLP engine")
            from core.nlp_engine import NLPEngine as BasicNLPEngine
            self.nlp_engine = BasicNLPEngine(self.config.get("nlp", {}))
        
        self.command_processor = CommandProcessor(self.config.get("command", {}))
        self.response_generator = ResponseGenerator(self.config.get("response", {}))
        
        # Initialize TTS engine
        self.tts_engine = TTSEngine(self.config.get("tts", {}))
        
        # State management
        self.is_running = False
        self.is_listening = False
        self.current_context = {}
        
        self.logger.info("Summer Assistant initialized")
    
    def start(self):
        """Start the assistant and begin listening for commands."""
        self.logger.info("Starting assistant")
        self.is_running = True
        self.is_listening = True
        
        # Main loop
        while self.is_running:
            try:
                # Listen for command
                if self.is_listening:
                    self.logger.info("Listening for command...")
                    command_text = self.listener.listen()
                    
                    if command_text:
                        self.process_command(command_text)
                
                # Small sleep to prevent CPU overuse
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                # Continue running despite errors
        
        self.shutdown()
    
    def process_command(self, command_text: str):
        """
        Process a command from text to execution.
        
        Args:
            command_text: The raw text of the command to process
        """
        self.logger.info(f"Processing command: {command_text}")
        
        try:
            # Use NLP to understand the command
            intent_data = self.nlp_engine.process(command_text, self.current_context)
            self.logger.debug(f"Intent recognized: {intent_data}")
            
            # Process the command based on the recognized intent
            result = self.command_processor.execute(intent_data, self.current_context)
            
            # Update context with the new information
            self.current_context.update(result.get("context_update", {}))
            
            # Generate response
            response = self.response_generator.generate(
                intent_data,
                result,
                self.current_context
            )
            
            # Output the response (both displayed and spoken)
            if response:
                self.logger.info(f"Response: {response}")
                print(f"Summer: {response}")
                
                # Speak the response if TTS is enabled
                self.tts_engine.speak(response)
        
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            error_response = self.response_generator.generate_error(str(e))
            print(f"Summer: {error_response}")
    
    def stop_listening(self):
        """Pause listening for commands."""
        self.is_listening = False
        self.logger.info("Listening paused")
    
    def resume_listening(self):
        """Resume listening for commands."""
        self.is_listening = True
        self.logger.info("Listening resumed")
    
    def shutdown(self):
        """Shutdown the assistant and release resources."""
        self.logger.info("Shutting down assistant")
        self.is_running = False
        self.is_listening = False
        
        # Clean up resources
        self.listener.shutdown()
        self.nlp_engine.shutdown()
        self.command_processor.shutdown()
        self.response_generator.shutdown()
        self.tts_engine.shutdown()
        
        self.logger.info("Assistant shutdown complete")