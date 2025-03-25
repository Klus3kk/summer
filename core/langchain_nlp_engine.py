"""
Summer AI Assistant - LangChain NLP Engine
---------------------------------------
Advanced NLP engine using LangChain for sophisticated intent recognition and reasoning.
"""

import logging
import os
import json
from typing import Dict, Any, Optional, List

try:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class LangChainNLPEngine:
    """
    Advanced NLP engine using LangChain for sophisticated understanding of commands.
    
    This class provides more advanced natural language processing capabilities,
    including context-aware command understanding and reasoning.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LangChain NLP engine with the specified configuration.
        
        Args:
            config: Configuration dictionary for the engine
        """
        self.logger = logging.getLogger("summer.langchain_nlp")
        self.config = config or {}
        
        # Check if LangChain is available
        if not LANGCHAIN_AVAILABLE:
            self.logger.error("LangChain library not found. This engine requires LangChain.")
            raise ImportError("LangChain library is required for this engine.")
        
        # Default configuration
        self.model_name = self.config.get("model_name", "gpt-4")
        self.temperature = self.config.get("temperature", 0.1)
        
        # OpenAI API key from config or environment
        self.api_key = self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            self.logger.error("OpenAI API key not found. This engine requires an API key.")
            raise ValueError("OpenAI API key is required for this engine.")
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )
        
        # Initialize conversation memory with input_key (IMPORTANT FIX)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="command"  # Set input_key to make multiple parameters work
        )
        
        # Generate format instructions
        format_instructions = """The output should be formatted as a JSON object with the following keys:
- intent: The identified intent (string)
- app_name: The target application name if applicable (string or null)
- parameters: Additional parameters for the command (object)
- confidence: Confidence score between 0 and 1 (number)

For example:
{
  "intent": "open_application",
  "app_name": "notepad",
  "parameters": {},
  "confidence": 0.9
}"""
        
        # Define the prompt template
        self.prompt = PromptTemplate(
            template="""You are an AI assistant that controls Windows applications through natural language commands.
            
Your task is to understand user commands and convert them into structured intents.

Available intents:
- open_application: Open a Windows application (requires app_name parameter)
- close_application: Close a Windows application (requires app_name parameter)
- write_text: Write text in an application (requires content parameter and optional app_name)
- draw_shape: Draw a shape in an application (requires shape parameter and optional app_name)
- search_web: Search the web for information (requires query parameter)
- system_command: Execute a system command (like volume control, brightness, etc.)

Here are examples of valid intents with their parameters:
1. "Open Notepad" -> {{"intent": "open_application", "app_name": "notepad", "parameters": {{}}, "confidence": 0.9}}
2. "Close Paint" -> {{"intent": "close_application", "app_name": "paint", "parameters": {{}}, "confidence": 0.9}}
3. "Write hello world in Notepad" -> {{"intent": "write_text", "app_name": "notepad", "parameters": {{"content": "hello world"}}, "confidence": 0.9}}
4. "Draw a circle in Paint" -> {{"intent": "draw_shape", "app_name": "paint", "parameters": {{"shape": "circle"}}, "confidence": 0.9}}

Previous conversation context:
{chat_history}

Current system state:
{system_state}

User command: {command}

Parse this into a structured command with an intent and parameters.

{format_instructions}

Only respond with the JSON object and nothing else.
""",
            input_variables=["command", "chat_history", "system_state"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        # Create the chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
        
        self.logger.info("LangChain NLP Engine initialized")
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a text command into a structured intent and parameters using LangChain.
        
        Args:
            text: The text to process
            context: Optional context information for better understanding
        
        Returns:
            A dictionary containing the recognized intent and parameters
        """
        context = context or {}
        self.logger.info(f"Processing text with LangChain: '{text}'")
        
        try:
            # Handle "Hello Summer" special case
            if text.lower() in ["hello summer", "hi summer", "hey summer"]:
                return {
                    "intent": "greeting",
                    "parameters": {"greeting": text},
                    "confidence": 1.0,
                    "original_text": text
                }
            
            # Convert context to a formatted string
            system_state = ""
            if context:
                system_state = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            else:
                system_state = "No specific context provided."
            
            # Execute the chain with properly named parameters
            response = self.chain.predict(
                command=text,
                system_state=system_state
            )
            
            # Parse the result
            try:
                # First see if it's valid JSON
                result = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON using string operations
                try:
                    # Look for JSON in markdown code blocks
                    if "```json" in response and "```" in response.split("```json", 1)[1]:
                        json_block = response.split("```json", 1)[1].split("```", 1)[0]
                        result = json.loads(json_block.strip())
                    elif "```" in response and "```" in response.split("```", 1)[1]:
                        json_block = response.split("```", 1)[1].split("```", 1)[0]
                        result = json.loads(json_block.strip())
                    else:
                        # Last resort: clean up the string and try again
                        cleaned_str = response.strip()
                        try:
                            result = json.loads(cleaned_str)
                        except:
                            self.logger.error("Could not parse JSON from response")
                            return {
                                "intent": "unknown",
                                "parameters": {},
                                "confidence": 0.0,
                                "original_text": text
                            }
                except Exception as e:
                    self.logger.error(f"Error extracting JSON: {e}")
                    return {
                        "intent": "unknown",
                        "parameters": {},
                        "confidence": 0.0,
                        "original_text": text
                    }
            
            # Parse the dictionary
            intent_data = {
                "intent": result.get("intent", "unknown"),
                "parameters": result.get("parameters", {}),
                "confidence": result.get("confidence", 0.5),
                "original_text": text
            }
            
            # If app_name exists, make sure it's in the parameters as well
            if "app_name" in result and result["app_name"]:
                intent_data["parameters"]["app_name"] = result["app_name"]
            
            # Fix parameter naming for specific intents
            self._fix_parameters(intent_data)
            
            return intent_data
                
        except Exception as e:
            self.logger.error(f"Error processing with LangChain: {e}")
            return {
                "intent": "unknown",
                "parameters": {},
                "confidence": 0.0,
                "original_text": text
            }
    
    def _fix_parameters(self, intent_data: Dict[str, Any]) -> None:
        """Fix parameter names to match what the command processor expects."""
        intent = intent_data.get("intent", "")
        parameters = intent_data.get("parameters", {})
        
        # For write_text intent, ensure content parameter is present
        if intent == "write_text":
            if "text" in parameters and "content" not in parameters:
                parameters["content"] = parameters["text"]
            elif not parameters.get("content"):
                parameters["content"] = intent_data.get("original_text", "")
        
        # For draw_shape intent, ensure shape parameter is present
        if intent == "draw_shape":
            if "type" in parameters and "shape" not in parameters:
                parameters["shape"] = parameters["type"]
    
    def shutdown(self):
        """Release resources and shutdown the engine."""
        self.logger.info("Shutting down LangChain NLP engine")
        # Nothing specific to clean up