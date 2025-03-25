"""
Summer AI Assistant - Paint Controller
------------------------------------
Controls the Windows Paint application.
"""

import logging
import time
import subprocess
import os
from typing import Dict, Any, Optional, Tuple

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class PaintController:
    """
    Controller for the Windows Paint application.
    
    This class handles operations related to Paint, such as:
    - Opening and closing Paint
    - Drawing shapes
    - Setting colors
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Paint controller with the specified configuration.
        
        Args:
            config: Configuration dictionary for the controller
        """
        self.logger = logging.getLogger("summer.apps.paint")
        self.config = config or {}
        
        # Check if pyautogui is available
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("pyautogui library not found. Some features may be limited.")
        
        # App-specific configuration
        self.app_path = self.config.get("app_path", "mspaint.exe")
        self.window_title = "Untitled - Paint"
        self.process = None
        
        # Define positions for various Paint controls (may need adjustment based on resolution)
        self.tools = {
            "pencil": {'key': 'p'},
            "brush": {'key': 'b'},
            "fill": {'key': 'f'},
            "text": {'key': 't'},
            "eraser": {'key': 'e'},
            "rectangle": {'key': 'r'},
            "circle": {'key': 'o'},
            "line": {'key': 'l'}
        }
        
        self.logger.info("Paint controller initialized")
    
    def open(self) -> Dict[str, Any]:
        """
        Open Paint.
        
        Returns:
            A dictionary containing the result of the operation
        """
        self.logger.info("Opening Paint")
        
        try:
            # Make sure the path is correct for mspaint.exe
            if not os.path.exists(self.app_path):
                # Try the default location if the configured path doesn't exist
                self.app_path = "mspaint.exe"
            
            # Launch Paint as a subprocess
            self.process = subprocess.Popen(self.app_path, shell=True)
            
            # Wait for the window to appear
            time.sleep(2.0)
            
            return {
                "success": True,
                "message": "Paint opened successfully"
            }
        except Exception as e:
            self.logger.error(f"Error opening Paint: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to open Paint"
            }
    
    def close(self) -> Dict[str, Any]:
        """
        Close Paint.
        
        Returns:
            A dictionary containing the result of the operation
        """
        self.logger.info("Closing Paint")
        
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
                    # Try to focus on Paint
                    self._focus_window()
                    # Send Alt+F4 to close
                    pyautogui.hotkey('alt', 'f4')
                    # If there are unsaved changes, handle the save dialog
                    time.sleep(0.5)
                    # If a dialog appears, press "Don't Save"
                    pyautogui.press('n')
                else:
                    # As a last resort, use taskkill
                    subprocess.run(["taskkill", "/f", "/im", "mspaint.exe"])
            
            return {
                "success": True,
                "message": "Paint closed successfully"
            }
        except Exception as e:
            self.logger.error(f"Error closing Paint: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to close Paint"
            }
    
    def draw_shape(self, shape: str, position: str = "center") -> Dict[str, Any]:
        """
        Draw a shape in Paint.
        
        Args:
            shape: The shape to draw (e.g., "square", "circle", "line")
            position: Where to draw the shape (e.g., "center", "top-left")
        
        Returns:
            A dictionary containing the result of the operation
        """
        self.logger.info(f"Drawing {shape} in Paint at {position}")
        
        if not PYAUTOGUI_AVAILABLE:
            return {
                "success": False,
                "error": "pyautogui not available",
                "message": "Cannot draw without pyautogui"
            }
        
        try:
            # Make sure Paint is open
            if not self._is_paint_running():
                self.open()
            
            # Focus on Paint window
            self._focus_window()
            
            # Clear existing content (Ctrl+A to select all, then delete)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            
            # Select the appropriate tool
            tool_key = None
            if shape.lower() in ["square", "rectangle"]:
                tool_key = self.tools["rectangle"]["key"]
            elif shape.lower() in ["circle", "oval"]:
                tool_key = self.tools["circle"]["key"]
            elif shape.lower() == "line":
                tool_key = self.tools["line"]["key"]
            else:
                # Default to pencil for other shapes
                tool_key = self.tools["pencil"]["key"]
            
            # Select the tool
            pyautogui.press(tool_key)
            
            # Get the drawing area coordinates
            canvas_coords = self._get_canvas_coordinates()
            
            # Calculate drawing coordinates based on position
            start_x, start_y, end_x, end_y = self._calculate_shape_coordinates(
                canvas_coords, shape, position
            )
            
            # Draw the shape
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y)
            pyautogui.mouseUp()
            
            return {
                "success": True,
                "message": f"Drew {shape} at {position}"
            }
        except Exception as e:
            self.logger.error(f"Error drawing in Paint: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to draw {shape} in Paint"
            }
    
    def _is_paint_running(self) -> bool:
        """
        Check if Paint is currently running.
        
        Returns:
            True if Paint is running, False otherwise
        """
        # A simple check by looking for the process
        try:
            output = subprocess.check_output(["tasklist", "/fi", "imagename eq mspaint.exe"])
            return b"mspaint.exe" in output
        except:
            return False
    
    def _focus_window(self) -> bool:
        """
        Focus on the Paint window.
        
        Returns:
            True if successfully focused, False otherwise
        """
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        try:
            # Try to find and focus on a window with "Paint" in the title
            windows = pyautogui.getWindowsWithTitle("Paint")
            if windows:
                windows[0].activate()
                time.sleep(0.2)  # Give it a moment to come to the foreground
                return True
            return False
        except:
            return False
    
    def _get_canvas_coordinates(self) -> Tuple[int, int, int, int]:
        """
        Get the coordinates of the Paint canvas area.
        
        Returns:
            A tuple containing (left, top, right, bottom) coordinates
        """
        # This is an approximation and may need adjustment based on Paint version and screen resolution
        if not PYAUTOGUI_AVAILABLE:
            return (0, 0, 0, 0)
        
        try:
            # Get the window
            windows = pyautogui.getWindowsWithTitle("Paint")
            if not windows:
                return (0, 0, 0, 0)
            
            window = windows[0]
            
            # Get window position and size
            left, top, width, height = window.left, window.top, window.width, window.height
            
            # Estimate the canvas area (excluding toolbars and menus)
            # These offsets are approximate and may need adjustment
            canvas_left = left + 10
            canvas_top = top + 100  # Account for title bar, menu, toolbars
            canvas_right = left + width - 10
            canvas_bottom = top + height - 10
            
            return (canvas_left, canvas_top, canvas_right, canvas_bottom)
        except:
            # Return full screen dimensions as a fallback
            screen_width, screen_height = pyautogui.size()