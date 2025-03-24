"""
Summer AI Assistant - Entry Point
--------------------------------
The main entry point for the Summer AI assistant.
"""

import os
import sys
import logging
import yaml
from dotenv import load_dotenv

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core components
from core.assistant import Assistant

def setup_logging():
    """Configure the logging system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('summer.log')
        ]
    )

def load_config():
    """Load configuration from the config.yml file."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

def main():
    """Main entry point for the Summer assistant."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger("summer")
    logger.info("Starting Summer AI Assistant")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Print a welcome message
        print("\n" + "=" * 50)
        print(f"  Summer AI Assistant v{config.get('assistant', {}).get('version', '0.1.0')}")
        print("  Your personal Windows AI assistant")
        print("=" * 50)
        print("  Say 'Hello Summer' to begin")
        print("  Press Ctrl+C to exit")
        print("=" * 50 + "\n")
        
        # Initialize the assistant with the loaded configuration
        assistant = Assistant(config)
        
        # Start the assistant
        assistant.start()
    except KeyboardInterrupt:
        logger.info("Summer AI Assistant stopped by user")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    finally:
        logger.info("Summer AI Assistant shutting down")

if __name__ == "__main__":
    main()