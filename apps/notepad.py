"""
Summer AI Assistant - Notepad Controller
--------------------------------------
Controls the Windows Notepad application.
"""

import logging
import time
import subprocess
import os
from typing import Dict, Any, Optional

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class NotepadController:
    """
    Controller for the Windows Notepad application.
    
    This class handles operations related to Notepad, such as:
    - Opening and closing Notepad
    - Writing text
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Notepad controller with the specified configuration.
        
        Args:
            config: Configuration dictionary for the controller
        """
        self.logger = logging.getLogger("summer.apps.notepad")
        self.config = config or {}
        
        # Check if pyautogui is available
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("pyautogui library not found. Some features may be limited.")
        
        # App-specific configuration
        self.app_path = self.config.get("app_path", "notepad.exe")
        self.window_title = "Untitled - Notepad"
        self.process = None
        
        self.logger.info("Notepad controller initialized")
    
    def open(self) -> Dict[str, Any]:
        """
        Open Notepad.
        
        Returns:
            A dictionary containing the result of the operation
        """
        self.logger.info("Opening Notepad")
        
        try:
            # Make sure the path is correct for notepad.exe
            if not os.path.exists(self.app_path):
                # Try the default location if the configured path doesn't exist
                self.app_path = "notepad.exe"
            
            # Launch Notepad as a subprocess with shell=True to ensure it works
            self.process = subprocess.Popen(self.app_path, shell=True)
            
            # Wait for the window to appear
            time.sleep(1.0)
            
            return {
                "success": True,
                "message": "Notepad opened successfully"
            }
        except Exception as e:
            self.logger.error(f"Error opening Notepad: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to open Notepad"
            }
    
    def close(self) -> Dict[str, Any]:
        """
        Close Notepad.
        
        Returns:
            A dictionary containing the result of the operation
        """
        self.logger.info("Closing Notepad")
        
        try:
            if self.process:
                # Try to terminate the process gracefully
                self.process.terminate()
                # Give it some time to close
                self.process.wait(timeout=2)
                self.process = None
            else:
                # If we don't have a reference to the process, use pyautogui
                if PYAUTOGUI_AVAILABLE:
                    # Try to focus on Notepad
                    self._focus_window()
                    # Send Alt+F4 to close
                    pyautogui.hotkey('alt', 'f4')
                    # If there are unsaved changes, handle the save dialog
                    time.sleep(0.5)
                    # If a dialog appears, press "Don't Save"
                    pyautogui.press('n')
                else:
                    # As a last resort, use taskkill
                    subprocess.run(["taskkill", "/f", "/im", "notepad.exe"])
            
            return {
                "success": True,
                "message": "Notepad closed successfully"
            }
        except Exception as e:
            self.logger.error(f"Error closing Notepad: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to close Notepad"
            }
    
    def write_text(self, text: str) -> Dict[str, Any]:
        """
        Write text in Notepad.
        
        Args:
            text: The text to write
        
        Returns:
            A dictionary containing the result of the operation
        """
        self.logger.info(f"Writing text in Notepad: {text}")
        
        if not PYAUTOGUI_AVAILABLE:
            return {
                "success": False,
                "error": "pyautogui not available",
                "message": "Cannot write text without pyautogui"
            }
        
        try:
            # Make sure Notepad is open
            if not self._is_notepad_running():
                self.open()
            
            # Focus on Notepad window
            self._focus_window()
            
            # Select all existing text (Ctrl+A) and delete it
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            
            # Type the new text
            pyautogui.write(text)
            
            return {
                "success": True,
                "message": f"Wrote text in Notepad"
            }
        except Exception as e:
            self.logger.error(f"Error writing in Notepad: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to write text in Notepad"
            }
    
    def _is_notepad_running(self) -> bool:
        """
        Check if Notepad is currently running.
        
        Returns:
            True if Notepad is running, False otherwise
        """
        # A simple check by looking for the process
        try:
            output = subprocess.check_output(["tasklist", "/fi", "imagename eq notepad.exe"])
            return b"notepad.exe" in output
        except:
            return False
    
    def _focus_window(self) -> bool:
        """
        Focus on the Notepad window.
        
        Returns:
            True if successfully focused, False otherwise
        """
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        try:
            # Try to find and focus on a window with "Notepad" in the title
            windows = pyautogui.getWindowsWithTitle("Notepad")
            if windows:
                windows[0].activate()
                time.sleep(0.2)  # Give it a moment to come to the foreground
                return True
            return False
        except:
            return False