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
    from langchain.output_parsers import PydanticOutputParser
    # Import directly from pydantic
    try:
        # Try Pydantic v2 import
        from pydantic import BaseModel, Field
    except ImportError:
        # Fall back to Pydantic v1 import
        from pydantic.v1 import BaseModel, Field
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class CommandIntent(BaseModel):
    """Pydantic model for parsed commands."""
    intent: str = Field(description="The identified intent of the command")
    app_name: Optional[str] = Field(None, description="The target application name if applicable")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the command")
    confidence: float = Field(description="Confidence score between 0 and 1")

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
        
        # Initialize the LLM first
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Generate format instructions manually instead of using PydanticOutputParser
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
- open_application: Open a Windows application
- close_application: Close a Windows application
- write_text: Write text in an application
- draw_shape: Draw a shape in an application
- search_web: Search the web for information
- system_command: Execute a system command (like volume control, brightness, etc.)

Previous conversation context:
{chat_history}

Current system state:
{system_state}

User command: {command}

Parse this into a structured command with an intent and parameters.

{format_instructions}
""",
            input_variables=["command", "chat_history", "system_state"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        # Create the chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=True,
            memory=self.memory
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
            # Convert context to a formatted string
            system_state = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            
            # Execute the chain
            response = self.chain.invoke({
                "command": text,
                "system_state": system_state or "No specific context provided."
            })
            
            # Extract the parsed result
            if isinstance(response, dict) and "text" in response:
                # Try to extract JSON from the response
                try:
                    # First see if it's already valid JSON
                    result = json.loads(response["text"])
                except json.JSONDecodeError:
                    # If not, try to extract JSON using string operations
                    json_str = response["text"]
                    # Find json block between ```json and ``` if exists
                    if "```json" in json_str and "```" in json_str.split("```json", 1)[1]:
                        json_block = json_str.split("```json", 1)[1].split("```", 1)[0]
                        result = json.loads(json_block.strip())
                    else:
                        # Last resort: try to clean up the string and parse it
                        # This is hacky but can sometimes recover from LLM formatting quirks
                        cleaned_str = json_str.strip()
                        if cleaned_str.startswith("```") and cleaned_str.endswith("```"):
                            cleaned_str = cleaned_str[3:-3].strip()
                        
                        # Try one more time
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
            
            else:
                # If no text field, use the whole response
                result = response
            
            # Parse the dictionary
            return {
                "intent": result.get("intent", "unknown"),
                "parameters": result.get("parameters", {}),
                "confidence": result.get("confidence", 0.5),
                "original_text": text
            }
                
        except Exception as e:
            self.logger.error(f"Error processing with LangChain: {e}")
            return {
                "intent": "unknown",
                "parameters": {},
                "confidence": 0.0,
                "original_text": text
            }
    
    def shutdown(self):
        """Release resources and shutdown the engine."""
        self.logger.info("Shutting down LangChain NLP engine")
        # Nothing specific to clean up