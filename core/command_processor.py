"""
Summer AI Assistant - Command Processor
-------------------------------------
Executes recognized intents by routing them to the appropriate handlers.
"""

import logging
import importlib
import os
from typing import Dict, Any, Optional, Callable, List, Tuple

# Placeholder controller for testing
class PlaceholderController:
    """Temporary placeholder for app controllers during development."""
    
    def __init__(self, app_name):
        self.app_name = app_name
        self.logger = logging.getLogger(f"summer.placeholder.{app_name}")
    
    def open(self):
        self.logger.info(f"[PLACEHOLDER] Opening {self.app_name}")
        return {"success": True}
    
    def close(self):
        self.logger.info(f"[PLACEHOLDER] Closing {self.app_name}")
        return {"success": True}
    
    def write_text(self, text):
        self.logger.info(f"[PLACEHOLDER] Writing in {self.app_name}: {text}")
        return {"success": True}
    
    def draw_shape(self, shape, position=None):
        self.logger.info(f"[PLACEHOLDER] Drawing {shape} in {self.app_name} at {position}")
        return {"success": True}

class CommandProcessor:
    """
    Processes recognized intents and routes them to the appropriate handlers.
    
    This class manages application controllers and executes commands by delegating
    to the appropriate controller based on the intent.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the command processor with the specified configuration.
        
        Args:
            config: Configuration dictionary for the command processor
        """
        self.logger = logging.getLogger("summer.command_processor")
        self.config = config or {}
        
        # Dictionary to store application controllers
        self.app_controllers = {}
        
        # Dictionary to map intents to handlers
        self.intent_handlers = {}
        
        # Register built-in intent handlers
        self._register_built_in_handlers()
        
        # Load application controllers
        self._load_app_controllers()
        
        self.logger.info("Command processor initialized")
    
    def _register_built_in_handlers(self):
        """Register the built-in intent handlers."""
        # Map intents to methods within this class
        self.intent_handlers = {
            "open_application": self._handle_open_application,
            "close_application": self._handle_close_application,
            "write_text": self._handle_write_text,
            "draw_shape": self._handle_draw_shape,
            "greeting": self._handle_greeting,
            "unknown": self._handle_unknown_intent,
            # Add more handlers as needed
        }
    
    def _load_app_controllers(self):
        """
        Load all available application controllers.
        
        This method dynamically loads controller classes from the apps directory.
        """
        try:
            # Get the apps directory
            apps_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "apps")
            
            # Import all Python files in the apps directory
            for filename in os.listdir(apps_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]  # Remove .py extension
                    
                    try:
                        # Import the module
                        module = importlib.import_module(f"apps.{module_name}")
                        
                        # Look for a class that matches the module name (CamelCase)
                        controller_class_name = "".join(word.capitalize() for word in module_name.split("_")) + "Controller"
                        
                        if hasattr(module, controller_class_name):
                            # Create an instance of the controller
                            controller_class = getattr(module, controller_class_name)
                            controller = controller_class(self.config.get(module_name, {}))
                            
                            # Store the controller
                            self.app_controllers[module_name] = controller
                            self.logger.info(f"Loaded controller for {module_name}")
                    
                    except Exception as e:
                        self.logger.error(f"Error loading controller {module_name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error loading app controllers: {e}")
            
        # Add controllers for apps that might not be dynamically loaded
        if "paint" not in self.app_controllers:
            try:
                # First try to import from apps
                from apps.paint import PaintController
                self.app_controllers["paint"] = PaintController(self.config.get("paint", {}))
                self.logger.info("Manually loaded controller for paint")
            except Exception as e:
                self.logger.error(f"Error loading Paint controller: {e}")
                self.app_controllers["paint"] = PlaceholderController("paint")
                
        if "notepad" not in self.app_controllers:
            try:
                # First try to import from apps
                from apps.notepad import NotepadController
                self.app_controllers["notepad"] = NotepadController(self.config.get("notepad", {}))
                self.logger.info("Manually loaded controller for notepad")
            except Exception as e:
                self.logger.error(f"Error loading Notepad controller: {e}")
                self.app_controllers["notepad"] = PlaceholderController("notepad")
        
        # For any controllers we still don't have, use placeholders
        for app in ["calculator", "browser", "system"]:
            if app not in self.app_controllers:
                self.app_controllers[app] = PlaceholderController(app)
                self.logger.warning(f"Using placeholder controller for {app}")
    
    def execute(self, intent_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a command based on the recognized intent.
        
        Args:
            intent_data: Dictionary containing intent and parameters
            context: Optional context information
        
        Returns:
            A dictionary containing the result of the execution
        """
        context = context or {}
        
        intent = intent_data.get("intent", "unknown")
        parameters = intent_data.get("parameters", {})
        
        self.logger.info(f"Executing intent: {intent} with parameters: {parameters}")
        
        # Look up the handler for this intent
        handler = self.intent_handlers.get(intent)
        
        if handler:
            try:
                # Call the handler with the parameters and context
                result = handler(parameters, context)
                return result
            except Exception as e:
                self.logger.error(f"Error executing intent {intent}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to execute {intent}"
                }
        else:
            self.logger.warning(f"No handler found for intent: {intent}")
            return {
                "success": False,
                "error": "Unknown intent",
                "message": f"I don't know how to handle {intent}"
            }
    
    def _get_app_controller(self, app_name: str):
        """
        Get the appropriate application controller based on the app name.
        
        Args:
            app_name: The name of the application
        
        Returns:
            The controller object, or None if not found
        """
        # Normalize the app name (remove spaces, lowercase)
        normalized_name = app_name.lower().replace(" ", "")
        
        # Map common variations to standard names
        app_name_mapping = {
            "notepad": "notepad",
            "note": "notepad",
            "notes": "notepad",
            "texteditor": "notepad",
            
            "paint": "paint",
            "mspaint": "paint",
            "drawing": "paint",
            
            "calc": "calculator",
            "calculator": "calculator",
            
            "browser": "browser",
            "chrome": "browser",
            "edge": "browser",
            "firefox": "browser",
            "web": "browser",
            
            "system": "system",
            "windows": "system",
            "computer": "system",
        }
        
        # Try to map the normalized name to a standard name
        standard_name = app_name_mapping.get(normalized_name)
        if standard_name:
            return self.app_controllers.get(standard_name)
        
        # If no mapping found, try direct lookup
        return self.app_controllers.get(normalized_name)
    
    def _handle_greeting(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting intents."""
        return {
            "success": True,
            "message": "Hello! I'm Summer, your personal Windows assistant. How can I help you today?",
            "context_update": {
                "last_action": "greeting"
            }
        }
    
    def _handle_draw_shape(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the draw_shape intent."""
        shape = parameters.get("shape", "")
        app_name = parameters.get("app_name", "")
        position = parameters.get("position", "center")
        
        if not shape:
            return {
                "success": False,
                "error": "Missing shape",
                "message": "I need to know what shape to draw."
            }
        
        if not app_name:
            # If no app specified, try to use the active app
            app_name = context.get("active_app")
            if not app_name:
                return {
                    "success": False,
                    "error": "No target application",
                    "message": "I need to know where to draw."
                }
        
        controller = self._get_app_controller(app_name)
        
        if controller:
            try:
                result = controller.draw_shape(shape, position)
                return {
                    "success": True,
                    "message": f"Drew {shape} in {app_name}",
                    "context_update": {
                        "active_app": app_name,
                        "last_action": "draw",
                        "last_shape": shape
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to draw in {app_name}"
                }
        else:
            return {
                "success": False,
                "error": "Unknown application",
                "message": f"I don't know how to draw in {app_name}"
            }
    
    def _handle_unknown_intent(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown intents."""
        return {
            "success": False,
            "error": "Unknown intent",
            "message": "I'm not sure what you want me to do. Could you be more specific?"
        }
    
    # Intent handlers
    
    def _handle_open_application(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the open_application intent.
        
        Args:
            parameters: Dictionary of parameters for the intent
            context: Current context information
        
        Returns:
            A dictionary containing the result
        """
        app_name = parameters.get("app_name", "")
        
        if not app_name:
            return {
                "success": False,
                "error": "Missing application name",
                "message": "I need to know which application to open."
            }
        
        # Get the controller for this application
        controller = self._get_app_controller(app_name)
        
        if controller:
            try:
                # Call the open method on the controller
                result = controller.open()
                
                # Update context
                return {
                    "success": True,
                    "message": f"Opened {app_name}",
                    "context_update": {
                        "active_app": app_name,
                        "app_state": "open"
                    }
                }
            except Exception as e:
                self.logger.error(f"Error opening {app_name}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to open {app_name}"
                }
        else:
            return {
                "success": False,
                "error": "Unknown application",
                "message": f"I don't know how to open {app_name}"
            }
    
    def _handle_close_application(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the close_application intent."""
        app_name = parameters.get("app_name", "")
        
        if not app_name:
            # If no app specified, try to close the active app
            app_name = context.get("active_app")
            if not app_name:
                return {
                    "success": False,
                    "error": "No active application",
                    "message": "I don't know which application to close."
                }
        
        controller = self._get_app_controller(app_name)
        
        if controller:
            try:
                result = controller.close()
                return {
                    "success": True,
                    "message": f"Closed {app_name}",
                    "context_update": {
                        "active_app": None,
                        "app_state": "closed"
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to close {app_name}"
                }
        else:
            return {
                "success": False,
                "error": "Unknown application",
                "message": f"I don't know how to close {app_name}"
            }
    
    def _handle_write_text(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the write_text intent."""
        content = parameters.get("content", "")
        app_name = parameters.get("app_name", "")
        
        if not content:
            return {
                "success": False,
                "error": "Missing content",
                "message": "I need to know what to write."
            }
        
        if not app_name:
            # If no app specified, try to use the active app
            app_name = context.get("active_app")
            if not app_name:
                return {
                    "success": False,
                    "error": "No target application",
                    "message": "I need to know where to write."
                }
        
        controller = self._get_app_controller(app_name)
        
        if controller:
            try:
                result = controller.write_text(content)
                return {
                    "success": True,
                    "message": f"Wrote text in {app_name}",
                    "context_update": {
                        "active_app": app_name,
                        "last_action": "write",
                        "last_content": content
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to write in {app_name}"
                }
        else:
            return {
                "success": False,
                "error": "Unknown application",
                "message": f"I don't know how to write in {app_name}"
            }