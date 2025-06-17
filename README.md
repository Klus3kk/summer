# Summer

## Overview

Summer is a voice-activated AI assistant that can control Windows applications and perform tasks based on natural language commands. Inspired by Jarvis from Iron Man (<3), Summer aims to provide a seamless interface between users and their Windows environment.

## Key Features

- **Voice Activation**: Speak naturally to control your computer
- **Natural Language Understanding**: Powered by LangChain and OpenAI's GPT models
- **Text-to-Speech**: Responds with a natural female voice using OpenAI's TTS technology
- **Application Control**: Open, close, and control Windows applications
- **Contextual Awareness**: Maintains context across interactions

## Supported Applications

- **Notepad**: Create and edit text documents
- **Paint**: Draw shapes and create artwork
- **Calculator**: Perform calculations 
- **Web Browsers**: Open websites and perform searches
- **System Controls**: Adjust volume, brightness, etc.

## Technical Architecture

Summer is built with a modular architecture:

- **Core Components**
  - Speech Recognition (input)
  - Natural Language Processing (understanding)
  - Command Processing (execution)
  - Text-to-Speech (output)

- **Technologies used**
  - **LangChain**: For sophisticated reasoning and command interpretation
  - **OpenAI GPT-4**: For advanced natural language understanding
  - **OpenAI TTS**: For lifelike voice responses

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows 10/11
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/summer.git
   cd summer
   ```

2. Create and activate a virtual environment:
   ```
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # For Windows Command Prompt:
   venv\Scripts\activate
   # For Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # For Git Bash or similar:
   source venv/Scripts/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create an `.env` file with your API keys:
   ```
   # Copy the example file
   cp .env.example .env
   
   # Edit the .env file and add your OpenAI API key
   # OPENAI_API_KEY=your-openai-api-key-here
   ```

5. Run the assistant:
   ```
   python main.py
   ```

6. Interact with Summer:
   - Say "Hello Summer" to begin
   - Press Ctrl+C to exit


## Configuration

Summer can be configured through the `config.yml` file:

- Voice settings (voice type, speaking style)
- NLP settings (model, temperature)
- Application paths
- Response style

## Usage Examples

- "Open Notepad and write a shopping list"
- "Draw a square in Paint at the center"
- "Calculate 2345 times 873"
- "Close all applications"

