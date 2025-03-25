"""
Summer AI Assistant - Response Generator
--------------------------------------
Generates appropriate responses based on intent results.
"""

import logging
import random
from typing import Dict, Any, Optional, List

class ResponseGenerator:
    """
    Generates appropriate responses to user commands based on the results.
    
    This class converts the structured result of command execution into
    natural language responses for the user.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the response generator with the specified configuration.
        
        Args:
            config: Configuration dictionary for the response generator
        """
        self.logger = logging.getLogger("summer.response_generator")
        self.config = config or {}
        
        # Load response templates
        self.templates = self._load_templates()
        
        self.logger.info("Response generator initialized")
    
    def _load_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load response templates for different result types.
        
        Returns:
            A dictionary mapping result types to lists of response templates
        """
        # In a full implementation, these could be loaded from a JSON file
        # For now, we'll define some basic templates inline
        return {
            "success": {
                "open_application": [
                    "I've opened {app_name} for you.",
                    "{app_name} is now open.",
                    "Launched {app_name}."
                ],
                "close_application": [
                    "I've closed {app_name}.",
                    "{app_name} is now closed.",
                    "Closed {app_name} as requested."
                ],
                "write_text": [
                    "I've written \"{content}\" in {app_name}.",
                    "Text entered in {app_name}.",
                    "Done! The text is now in {app_name}."
                ],
                "draw_shape": [
                    "I've drawn a {shape} in {app_name}.",
                    "Created a {shape} as requested.",
                    "There you go, a {shape} in {app_name}."
                ],
                "greeting": [
                    "Hello! I'm Summer, your personal Windows assistant. How can I help you today?",
                    "Hi there! I'm Summer. What can I do for you?",
                    "Hello! Summer assistant at your service. What would you like me to do?"
                ],
                "default": [
                    "Done!",
                    "Task completed successfully.",
                    "I've done that for you."
                ]
            },
            "error": {
                "unknown_application": [
                    "I don't know how to work with {app_name}.",
                    "Sorry, I'm not familiar with {app_name}.",
                    "I can't control {app_name} yet."
                ],
                "unknown_intent": [
                    "I'm not sure what you want me to do.",
                    "Could you be more specific?",
                    "I didn't understand that command."
                ],
                "default": [
                    "I encountered a problem: {error}",
                    "Sorry, I couldn't do that: {error}",
                    "There was an issue: {error}"
                ]
            }
        }
    
    def generate(self, 
                intent_data: Dict[str, Any], 
                result: Dict[str, Any], 
                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a natural language response based on the intent and result.
        
        Args:
            intent_data: The recognized intent data
            result: The result of executing the command
            context: Optional context information
        
        Returns:
            A natural language response
        """
        context = context or {}
        
        intent = intent_data.get("intent", "unknown")
        parameters = intent_data.get("parameters", {})
        
        # Determine if the result was successful
        success = result.get("success", False)
        
        # Get the appropriate template category
        if success:
            templates = self.templates["success"]
            # Try to get templates specific to this intent
            response_templates = templates.get(intent, templates["default"])
        else:
            templates = self.templates["error"]
            error_type = result.get("error_type", "default")
            response_templates = templates.get(error_type, templates["default"])
        
        # Select a random template
        template = random.choice(response_templates)
        
        # Combine all available parameters for formatting
        format_params = {**parameters, **result}
        
        # Special handling for certain parameters
        if "app_name" in parameters:
            format_params["app_name"] = parameters["app_name"].title()
        
        if "shape" in parameters:
            format_params["shape"] = parameters["shape"].lower()
        
        # Format the template with the parameters
        try:
            response = template.format(**format_params)
        except KeyError as e:
            self.logger.error(f"Missing parameter in template: {e}")
            # Fall back to the result message
            response = result.get("message", "Task completed.")
        
        return response
    
    def generate_error(self, error_message: str) -> str:
        """
        Generate a response for an unexpected error.
        
        Args:
            error_message: The error message
        
        Returns:
            A natural language response
        """
        templates = [
            "Sorry, I encountered an error: {error}",
            "There was a problem: {error}",
            "I couldn't complete that action because: {error}"
        ]
        
        template = random.choice(templates)
        return template.format(error=error_message)
    
    def shutdown(self):
        """Release resources and shutdown the response generator."""
        self.logger.info("Shutting down response generator")
        # Nothing specific to clean up in this implementation