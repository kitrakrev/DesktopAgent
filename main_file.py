
"""
## Setup

To install the dependencies for this script, run:

``` 
pip install google-genai opencv-python pyaudio pillow mss python-dotenv pynput pyautogui
```

Before running this script, ensure the `GOOGLE_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

Important: **Use headphones**. This script uses the system default audio
input and output, which often won't include echo cancellation. So to prevent
the model from interrupting itself it is important that you use headphones. 

## Run

To run the script:

```
python Get_started_LiveAPI.py
```

The script takes a video-mode flag `--mode`, this can be "camera", "screen", or "none".
The default is "camera". To share your screen run:

```
python Get_started_LiveAPI.py --mode screen
```
"""

import asyncio
import base64
import io
import os
import sys
import traceback

import cv2
import pyaudio
import PIL.Image
import mss

import argparse

from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
from PIL import ImageDraw
import pyautogui
if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "gemini-2.5-flash-native-audio-preview-09-2025"

DEFAULT_MODE = "camera"
from pynput import mouse
from pynput import keyboard
import pyautogui
import mss
import numpy as np
import cv2
client = genai.Client(api_key=GOOGLE_API_KEY)

# Global mouse controller for reliability (avoids creating new instances)
_MOUSE_CONTROLLER = mouse.Controller()


def capture_screen_sync():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            return np.array(sct.grab(monitor))
    except Exception as e:
        raise RuntimeError(
            "❌ Screen capture failed! On macOS, grant Screen Recording permission:\n"
            "  → System Settings → Privacy & Security → Screen Recording\n"
            "  → Add Terminal (or your IDE)\n"
            f"Original error: {e}"
        )

import os
import time
import cv2
import numpy as np
import threading
import mss
from google import genai
from google.genai import types


def show_quiz_modal(quiz_text):
    """
    Display quiz in a translucent modal window that can be closed.
    Must be called from the main thread (macOS requirement).
    """
    import tkinter as tk
    from tkinter import font as tkfont

    # Create the main window
    root = tk.Tk()
    root.title("🎯 Quiz Time!")

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size (60% of screen)
    window_width = int(screen_width * 0.6)
    window_height = int(screen_height * 0.6)

    # Center window
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Make window translucent and always on top
    root.attributes('-alpha', 0.95)
    root.attributes('-topmost', True)

    # Colors
    bg_color = "#2C3E50"
    text_color = "#ECF0F1"
    accent_color = "#3498DB"

    root.configure(bg=bg_color)
    content_frame = tk.Frame(root, bg=bg_color, padx=30, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
    title_label = tk.Label(content_frame, text="🎯 Quiz Time! 🎯",
                           font=title_font, bg=bg_color, fg=accent_color)
    title_label.pack(pady=(0, 20))

    # Quiz text box
    quiz_font = tkfont.Font(family="Helvetica", size=14)
    quiz_text_widget = tk.Text(content_frame, font=quiz_font, bg="#34495E",
                               fg=text_color, wrap=tk.WORD, padx=20, pady=20,
                               relief=tk.FLAT, highlightthickness=0)
    quiz_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    quiz_text_widget.insert(1.0, quiz_text)
    quiz_text_widget.config(state=tk.DISABLED)

    # Close button
    def close_window():
        root.destroy()

    button_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
    close_button = tk.Button(content_frame, text="✖ Close Quiz",
                             command=close_window, font=button_font,
                             bg="#E74C3C", fg="white",
                             activebackground="#C0392B",
                             activeforeground="white",
                             relief=tk.FLAT, padx=20, pady=10, cursor="hand2")
    close_button.pack()

    root.bind('<Escape>', lambda e: close_window())
    root.mainloop()


def generate_quiz_from_screen():
    """
    Capture the current screen and generate a fun quiz with:
    - 2 questions about what's visible on screen
    - 1 fun/creative question for entertainment

    Displays in a translucent modal window if on main thread,
    otherwise prints to console (safe for async/threaded contexts).
    """
    import inspect

    try:
        print("[LOG] Starting quiz generation...")

        # Capture screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            img = np.array(sct.grab(monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Save screenshot
            save_dir = f"quiz_screens_{int(time.time())}"
            os.makedirs(save_dir, exist_ok=True)
            screenshot_path = f"{save_dir}/screen.jpg"
            cv2.imwrite(screenshot_path, img)

        print(f"[LOG] Screenshot saved at: {screenshot_path}")

        # Read image for Gemini
        with open(screenshot_path, "rb") as f:
            image_bytes = f.read()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable.")

        print("[LOG] Connecting to Gemini API...")
        quiz_client = genai.Client(api_key=api_key)

        # Generate quiz using Gemini
        response = quiz_client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                types.Part.from_text(
                    text="""Analyze this screenshot and create a fun quiz with exactly 3 questions:

1. SCREEN QUESTION 1: Ask about something specific visible in the screenshot (text, UI element, content, etc.)
2. SCREEN QUESTION 2: Ask another question about different content visible in the screenshot
3. FUN QUESTION: Ask a creative, humorous, or thought-provoking question inspired by what you see (can be playful!)

Format each question clearly with:
Question 1: [Your question here]
Question 2: [Your question here]  
Question 3 (Fun): [Your question here]

Make the questions engaging and fun!"""
                )
            ]
        )

        quiz_text = response.text.strip()

        # Print to console
        print("\n" + "=" * 60)
        print("🎯 QUIZ TIME! 🎯")
        print("=" * 60)
        print(quiz_text)
        print("=" * 60 + "\n")

        # Only show GUI if on main thread
        if threading.current_thread() is threading.main_thread():
            print("[LOG] On main thread — showing Tkinter modal.")
            show_quiz_modal(quiz_text)
        else:
            print("[LOG] Not on main thread — skipping GUI, printing to console only.")

        return {
            "result": "Quiz generated successfully!",
            "quiz": quiz_text,
            "screenshot": screenshot_path
        }

    except Exception as e:
        import traceback
        print("[ERROR] Quiz generation failed:", e)
        print(traceback.format_exc())
        return {"error": f"Failed to generate quiz: {str(e)}"}

def smart_detect_screen_coordinates(prompt):
    """
    Capture the screen, draw a grid with numbered coordinates,
    save three images:
      1️⃣ Original screen (no grid)
      2️⃣ Screen with grid overlay
      3️⃣ Pure grid only (no background)
    Send both the grid and original to Gemini 2.5 Pro,
    and return (x, y) coordinates.
    """
    import os
    import time
    import cv2
    import numpy as np
    # from mss import mss
    from google import genai
    from google.genai import types

    # === Setup ===
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable.")

    client = genai.Client(api_key=api_key)
    save_dir = f"screens_{int(time.time())}"
    os.makedirs(save_dir, exist_ok=True)
    step = 25

    original_path = f"{save_dir}/screen.jpg"
    grid_path = f"{save_dir}/screen_grid.jpg"
    pure_grid_path = f"{save_dir}/grid_only.jpg"

    # === Capture Screen ===
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Full primary screen
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        cv2.imwrite(original_path, img)

    # === Draw Grid Overlay ===
    grid_img = img.copy()
    height, width, _ = grid_img.shape

    def draw_grid(base_img, color=(90, 90, 90)):
        """Draws grid lines and coordinate labels."""
        for x in range(0, width, step):
            cv2.line(base_img, (x, 0), (x, height), color, 1)
            cv2.putText(base_img, str(x), (x + 2, 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(base_img, str(x), (x + 2, height - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        for y in range(0, height, step):
            cv2.line(base_img, (0, y), (width, y), color, 1)
            cv2.putText(base_img, str(y), (5, y + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(base_img, str(y), (width - 40, y + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        return base_img

    # Apply to overlay image
    grid_img = draw_grid(grid_img)
    cv2.imwrite(grid_path, grid_img)

    # === Pure Grid Only (white background) ===
    pure_grid = np.ones_like(img, dtype=np.uint8) * 255
    pure_grid = draw_grid(pure_grid, color=(0, 0, 0))
    cv2.imwrite(pure_grid_path, pure_grid)

    print(f"📸 Saved images:\n  • Original: {original_path}\n  • Grid: {grid_path}\n  • Pure grid: {pure_grid_path}")

    # === Send to Gemini ===
    with open(original_path, "rb") as f1, open(grid_path, "rb") as f2, open(pure_grid_path, "rb") as f3:
        original_bytes = f1.read()
        grid_bytes = f2.read()
        pure_grid_bytes = f3.read()

    # ✅ Use correct Part syntax for SDK >=0.6
    response = client.models.generate_content(
        model="models/gemini-2.5-pro",
        contents=[
            types.Part.from_bytes(data=original_bytes, mime_type="image/jpeg"),
            types.Part.from_bytes(data=grid_bytes, mime_type="image/jpeg"),
            types.Part.from_bytes(data=pure_grid_bytes, mime_type="image/jpeg"),
            types.Part.from_text(
                text=f"Find the coordinates of the object '{prompt}' using the grid reference. "
                     f"Use the pure grid for scale and precision. Return only the coordinates in format x=___, y=___."
            )
        ]
    )

    text = response.text.strip()
    print("🔍 Model output:", text)
    return {"result": text}

def get_screen_size():
    """Get the screen size."""
    return {"width": pyautogui.size()[0], "height": pyautogui.size()[1]}

def get_mouse_position():
    """Get the mouse position."""
    return {"x": _MOUSE_CONTROLLER.position[0], "y": _MOUSE_CONTROLLER.position[1]}

def move_mouse_relative(x: int, y: int):
    """Move the mouse relative to the current position. x is the horizontal distance to move and y is the vertical distance to move.
    x is the distance from the left edge of the screen and y is the distance from the top edge of the screen.
    So get the current mouse position first, then add the x and y to the current position.
    """
    current_x, current_y = _MOUSE_CONTROLLER.position
    _MOUSE_CONTROLLER.position = (int(current_x + x), int(current_y + y))
    return {"result": f"mouse current position is {_MOUSE_CONTROLLER.position}"}
def move_mouse_absolute(x, y):
    import time
    start_x, start_y = _MOUSE_CONTROLLER.position
    steps = 20
    delay = 0.005
    for i in range(1, steps + 1):
        nx = int(start_x + (x - start_x) * i / steps)
        ny = int(start_y + (y - start_y) * i / steps)
        _MOUSE_CONTROLLER.position = (nx, ny)
        time.sleep(delay)
    return {"result": f"Mouse moved smoothly to {(x, y)}"}
    
def left_click_mouse(count: int = 1):
    """Left click the mouse button once."""
    _MOUSE_CONTROLLER.click(mouse.Button.left, count)
    return {"result": f"left clicked the mouse button {count} times"}

def right_click_mouse(count: int = 1):
    """Right click the mouse button once."""
    _MOUSE_CONTROLLER.click(mouse.Button.right, count)
    return {"result": f"right clicked the mouse button {count} times"}

def scroll_mouse_by(dx: int, dy: int):
    """
    Scroll the mouse by the given amounts.
    dx: horizontal scroll steps (positive -> right)
    dy: vertical scroll steps (positive -> up)
    Uses pynput.mouse.Controller.scroll(dx, dy).
    """
    mouse.Controller().scroll(dx, dy)
    return {"result": f"scrolled by dx={dx}, dy={dy}"}


def press_key(key: str):
    """Press the given key. key is the key to press. key is a string of the key to press.
    """
    special_keys = {
        "space": keyboard.Key.space,
        "enter": keyboard.Key.enter,
        "shift": keyboard.Key.shift,
        "ctrl": keyboard.Key.ctrl,
        "alt": keyboard.Key.alt,
        "cmd": keyboard.Key.cmd,
        "tab": keyboard.Key.tab,
        "esc": keyboard.Key.esc,
        "up": keyboard.Key.up,
        "down": keyboard.Key.down,
        "left": keyboard.Key.left,
        "right": keyboard.Key.right,
        "backspace": keyboard.Key.backspace,
        "delete": keyboard.Key.delete,
    }
    if key in special_keys:
        keyboard.Controller().press(special_keys[key])
    else:
        keyboard.Controller().press(key)
    return {"result": f"pressed the key {key}"}

import platform
import time
from pynput import keyboard

def type_text(text: str, select_all_first: bool = False):
    """
    Type text at the current cursor position.
    If select_all_first is True, will select all existing text (Cmd/Ctrl+A, Delete) before typing.
    """
    _keyboard = keyboard.Controller()
    system = platform.system().lower()

    try:
        if select_all_first:
            modifier = keyboard.Key.cmd if system == "darwin" else keyboard.Key.ctrl

            # Select all (Cmd/Ctrl + A)
            with _keyboard.pressed(modifier):
                _keyboard.press('a')
                _keyboard.release('a')
            time.sleep(0.05)

            # Delete selected text
            _keyboard.press(keyboard.Key.delete)
            _keyboard.release(keyboard.Key.delete)
            time.sleep(0.05)

        # Type new text
        _keyboard.type(text)

        return {
            "result": f"Typed: '{text}'" + (" (replaced existing text)" if select_all_first else "")
        }

    except Exception as e:
        return {"error": f"Failed to type text: {str(e)}"}


def select_all_and_replace(text: str):
    """
    Select all text in the current field (Cmd/Ctrl+A) and replace it with new text.
    Works on macOS, Windows, and Linux.
    """
    return type_text(text, select_all_first=True)

def press_key_combination(keys: list):
    """
    Press a combination of keys simultaneously (e.g., Cmd+C, Cmd+V).
    keys: list of key names to press together.
    Example: ["cmd", "c"] for copy, ["cmd", "v"] for paste.
    """
    _keyboard = keyboard.Controller()
    special_keys = {
        "space": keyboard.Key.space,
        "enter": keyboard.Key.enter,
        "shift": keyboard.Key.shift,
        "ctrl": keyboard.Key.ctrl,
        "alt": keyboard.Key.alt,
        "cmd": keyboard.Key.cmd,
        "tab": keyboard.Key.tab,
        "esc": keyboard.Key.esc,
        "backspace": keyboard.Key.backspace,
        "delete": keyboard.Key.delete,
    }
    
    try:
        # Convert string keys to Key objects
        key_objects = []
        for key in keys:
            if key in special_keys:
                key_objects.append(special_keys[key])
            else:
                key_objects.append(key)
        
        # Press all keys
        for key in key_objects[:-1]:
            _keyboard.press(key)
        
        # Press and release the last key
        _keyboard.press(key_objects[-1])
        _keyboard.release(key_objects[-1])
        
        # Release all modifier keys in reverse order
        for key in reversed(key_objects[:-1]):
            _keyboard.release(key)
        
        return {"result": f"Pressed key combination: {' + '.join(keys)}"}
    except Exception as e:
        return {"error": f"Failed to press key combination: {str(e)}"}

def hold_left_mouse_button():
    """Hold the left mouse button down."""
    mouse.Controller().press(mouse.Button.left)
    return {"result": f"held the left mouse button down"}
def release_left_mouse_button():
    """Release the left mouse button."""
    mouse.Controller().release(mouse.Button.left)
    return {"result": f"released the left mouse button"}
def hold_right_mouse_button():
    """Hold the right mouse button down."""
    mouse.Controller().press(mouse.Button.right)
    return {"result": f"held the right mouse button down"}
def release_right_mouse_button():
    """Release the right mouse button."""
    mouse.Controller().release(mouse.Button.right)
    return {"result": f"released the right mouse button"}
# def get_screen_with_grid():
#     """Capture the screen, draw a 25px grid, and mark coordinates."""
#     sct = mss.mss()
#     monitor = sct.monitors[0]
#     screenshot = sct.grab(monitor)
#     img = PIL.Image.frombytes("RGB", screenshot.size, screenshot.rgb)
#     draw = ImageDraw.Draw(img)

#     width, height = img.size
#     step = 25
#     font_color = (0, 255, 0)
#     grid_color = (50, 255, 50)
#     text_offset = 5

#     # Draw vertical and horizontal grid lines every 50px
#     for x in range(0, width, step):
#         draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
#         if (x // step) % 2 == 0:  # Label every alternate vertical line
#             draw.text((x + text_offset, 5), str(x), fill=font_color)

#     for y in range(0, height, step):
#         draw.line([(0, y), (width, y)], fill=grid_color, width=1)
#         if (y // step) % 2 == 0:  # Label every alternate horizontal line
#             draw.text((5, y + text_offset), str(y), fill=font_color)

#     # Optional: highlight current mouse cursor
#     mx, my = pyautogui.position()
#     cursor_color = (255, 80, 0)
#     draw.ellipse(
#         (mx - 6, my - 6, mx + 6, my + 6),
#         fill=cursor_color,
#         outline=(255, 200, 0),
#         width=2,
#     )

#     # Save for debugging (optional)
#     import time
#     img.save(f"screen_grid_{int(time.time())}.jpeg", format="JPEG", quality=70, optimize=True)

#     # Prepare for streaming
#     image_io = io.BytesIO()
#     img.save(image_io, format="jpeg", quality=65, optimize=True)
#     image_io.seek(0)
#     return {
#         "mime_type": "image/jpeg",
#         "data": base64.b64encode(image_io.read()).decode(),
#     }


func_names_dict = {
    "move_mouse_relative": move_mouse_relative,
    "move_mouse_absolute": move_mouse_absolute,
    "left_click_mouse": left_click_mouse,
    "right_click_mouse": right_click_mouse,
    "hold_left_mouse_button": hold_left_mouse_button,
    "release_left_mouse_button": release_left_mouse_button,
    "hold_right_mouse_button": hold_right_mouse_button,
    "release_right_mouse_button": release_right_mouse_button,
    "scroll_mouse_by": scroll_mouse_by,
    "press_key": press_key,
    "type_text": type_text,
    "select_all_and_replace": select_all_and_replace,
    "press_key_combination": press_key_combination,
    "get_screen_size": get_screen_size,
    "get_mouse_position": get_mouse_position,
    "generate_quiz_from_screen": generate_quiz_from_screen,
    # "get_screen_with_grid": get_screen_with_grid
    "smart_detect_screen_coordinates": smart_detect_screen_coordinates
}



tools = [
   types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="move_mouse_relative",
            description="Move the mouse to the given coordinates.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"x": types.Schema(type=types.Type.NUMBER), "y": types.Schema(type=types.Type.NUMBER)})
        ),
        types.FunctionDeclaration(
            name="hold_left_mouse_button",
            description="Hold the left mouse button down.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="release_left_mouse_button",
            description="Release the left mouse button.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="hold_right_mouse_button",
            description="Hold the right mouse button down.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="release_right_mouse_button",
            description="Release the right mouse button.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="move_mouse_absolute",
            description="Call get screen_size before calling this function. Move the mouse to the given coordinates. x is the horizontal coordinate and y is the vertical coordinate. x is the distance from the left edge of the screen and y is the distance from the top edge of the screen.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"x": types.Schema(type=types.Type.NUMBER), "y": types.Schema(type=types.Type.NUMBER)})
        ),
        types.FunctionDeclaration(
            name="left_click_mouse",
            description= "Left click the mouse button once. count is the number of times to click the mouse button. count is an optional parameter and default is 1.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"count": types.Schema(type=types.Type.NUMBER)})
        ),
        types.FunctionDeclaration(
            name="right_click_mouse",
            description="Right click the mouse button once.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"count": types.Schema(type=types.Type.NUMBER)})
        ),
        types.FunctionDeclaration(
            name="scroll_mouse_by",
            description="Scroll the mouse by the given amounts. dx is the horizontal scroll steps (positive -> right) and dy is the vertical scroll steps (positive -> up).",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"dx": types.Schema(type=types.Type.NUMBER), "dy": types.Schema(type=types.Type.NUMBER)})
        ),
        types.FunctionDeclaration(
            name="press_key",
            description="Press the given key. key is a string of the key to press. key is a special key or a regular key. special keys are space, enter, shift, ctrl, alt, cmd, tab, esc, up, down, left, right, backspace, delete. regular keys are the keys on the keyboard.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"key": types.Schema(type=types.Type.STRING)})
        ),
        types.FunctionDeclaration(
            name="type_text",
            description="Type text at the current cursor position. If select_all_first is True, will select all existing text (Cmd+A) before typing to replace it. Very useful for filling forms or replacing text in input fields.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={
                "text": types.Schema(type=types.Type.STRING, description="The text to type"),
                "select_all_first": types.Schema(type=types.Type.BOOLEAN, description="If True, select all text before typing (replaces existing text). Default is False.")
            }, required=["text"])
        ),
        types.FunctionDeclaration(
            name="select_all_and_replace",
            description="Select all text in the current field (Cmd+A) and replace it with new text. Perfect for replacing text in input fields, text boxes, or editors.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={
                "text": types.Schema(type=types.Type.STRING, description="The new text to replace with")
            }, required=["text"])
        ),
        types.FunctionDeclaration(
            name="press_key_combination",
            description="Press a combination of keys simultaneously. Useful for keyboard shortcuts like Cmd+C (copy), Cmd+V (paste), Cmd+S (save), etc. Keys are pressed in order and released in reverse order.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={
                "keys": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="List of keys to press together. Example: ['cmd', 'c'] for copy, ['cmd', 'v'] for paste, ['cmd', 'shift', 's'] for save as.")
            }, required=["keys"])
        ),
        types.FunctionDeclaration(
            name="get_screen_size",
            description="Get the screen size.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_mouse_position",
            description="Get the mouse position.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        # types.FunctionDeclaration(
        #     name="get_screen_with_grid",
        #     description="Get the screen with a custom visible cursor overlay and a 25px grid. This function is used to help the screen capture and the mouse position. Call this function before decideding on coordinates to move the mouse to.",
        #     parameters=types.Schema(type=types.Type.OBJECT, properties={})
        # )
        types.FunctionDeclaration(
            name="smart_detect_screen_coordinates",
            description="Smart detect the screen coordinates based on the prompt. Call this function before decideding on coordinates to move the mouse to.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={"prompt": types.Schema(type=types.Type.STRING)})
        ),
        types.FunctionDeclaration(
            name="generate_quiz_from_screen",
            description="Generate a fun quiz based on what's currently visible on screen! Creates 2 questions about screen content and 1 creative/fun question. Perfect for entertainment, learning, or testing knowledge about what's displayed. The AI will analyze the screen and create engaging questions.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        )
    ]
   )
]




CONFIG = {"response_modalities": ["AUDIO"], "tools": tools
,
    "system_instruction": """You are an assistant that controls the user's mouse and keyboard based on voice commands.

CRITICAL WORKFLOW - When clicking on UI elements, ALWAYS follow this sequence:
1. FIRST: Call smart_detect_screen_coordinates(prompt="description of element") to find the coordinates
2. SECOND: Extract the x,y coordinates from the result (format: "x=123, y=456")
3. THIRD: Call move_mouse_absolute(x, y) to move the mouse to those coordinates
4. FOURTH: Call left_click_mouse() to click at that position

NEVER skip step 3! The mouse must move to the detected coordinates before clicking.

General rules:
- Always use smart_detect_screen_coordinates when you don't know exact coordinates - never guess!
- Be precise and confirm each action verbally
- Break complex tasks into smaller steps and execute one by one
- If something is not possible, say so and don't try to do it
- Use all available tools in the correct order and sequence
     """
}

pya = pyaudio.PyAudio()

class AudioLoop:
    def __init__(self, video_mode=DEFAULT_MODE):
        self.video_mode = video_mode

        self.audio_in_queue = None
        self.out_queue = None

        self.session = None

        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None

    async def send_text(self):
        while True:
            text = await asyncio.to_thread(
                input,
                "message > ",
            )
            if text.lower() == "q":
                break
            await self.session.send_client_content(
    turns=[{'role': 'user', 'parts': [{'text': text or "."}]}],
    turn_complete=True
)

    def _get_frame(self, cap):
        # Read the frameq
        ret, frame = cap.read()
        # Check if the frame was read successfully
        if not ret:
            return None
        # Fix: Convert BGR to RGB color space
        # OpenCV captures in BGR but PIL expects RGB format
        # This prevents the blue tint in the video feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)  # Now using RGB frame
        img.thumbnail([1024, 1024])
        
        image_io = io.BytesIO()
        img.save(image_io, format="jpeg", quality=85)
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        # This takes about a second, and will block the whole program
        # causing the audio pipeline to overflow if you don't to_thread it.
        cap = await asyncio.to_thread(
            cv2.VideoCapture, 0
        )  # 0 represents the default camera

        while True:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break

            await asyncio.sleep(0.1)

            await self.out_queue.put(frame)

        # Release the VideoCapture object
        cap.release()



    def _get_screen(self):
        """Capture screen and draw a custom visible cursor overlay."""
        with mss.mss() as sct:
            monitor = sct.monitors[0]

            # Grab the screen
            screenshot = sct.grab(monitor)

            # Convert to a Pillow image
            img = PIL.Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            # === Draw the cursor overlay ===
            mx, my = pyautogui.position()
            draw = ImageDraw.Draw(img)

            # Choose cursor style
            cursor_color = (255, 80, 0)  # Orange-red
            ring_radius = 12
            inner_radius = 4

            # Glowing ring effect
            for r in range(ring_radius + 6, ring_radius, -2):
                draw.ellipse(
                    (mx - r, my - r, mx + r, my + r),
                    outline=(255, 120, 0),
                    width=1
                )

            # Main cursor circle
            draw.ellipse(
                (mx - inner_radius, my - inner_radius, mx + inner_radius, my + inner_radius),
                fill=cursor_color
            )

            # Optional: crosshair center
            draw.line((mx - 6, my, mx + 6, my), fill=(255, 200, 0), width=2)
            draw.line((mx, my - 6, mx, my + 6), fill=(255, 200, 0), width=2)

            # === Optimize for streaming ===
            image_io = io.BytesIO()
            img.save(image_io, format="JPEG", quality=85)
            image_io.seek(0)

            return {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_io.read()).decode(),
            }

    async def get_screen(self):

        while True:
            frame = await asyncio.to_thread(self._get_screen)
            if frame is None:
                break

            await asyncio.sleep(2.0)

            await self.out_queue.put(frame)

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(media=msg)

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def receive_audio(self,tg: asyncio.TaskGroup,session):
        "Background task to reads from the websocket and write pcm chunks to the output queue"
        while True:
            turn = self.session.receive()
            response = None
            try:
                async for response in turn:
                    if data := response.data:
                        self.audio_in_queue.put_nowait(data)
                        continue
                    elif text := response.text:
                        print(text, end="")
                    elif tool_call := response.tool_call:
                        await self.handle_tool_call(session, tool_call)
                    elif setup_complete := response.setup_complete:
                        print(response)
                    elif turn_complete := response.server_content.turn_complete:
                        print(response)
                    elif generation_complete := response.server_content.generation_complete:
                        print(response)
                    elif response_complete := response.server_content.interrupted:
                        print(response)
                    elif len(response.server_content.model_turn.parts) > 0:
                        print(response)
                    
                    else:
                        print('>>> ', response)
            except Exception as e:
                print("Response: ", response)
                print('>>> Error: ', e)
                        
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

        
    async def handle_tool_call(self, session, tool_call):
        print("Tool call: ", tool_call)
        function_responses = []
        for fc in tool_call.function_calls:
            try:
                result = func_names_dict[fc.name](**fc.args)
                function_responses.append(types.FunctionResponse(
                    id=fc.id,
                    name=fc.name,
                    response=result,
                ))
            except Exception as e:
                print(f"❌ Tool {fc.name} failed: {e}")
                function_responses.append(types.FunctionResponse(
                    id=fc.id,
                    name=fc.name,
                    response={"error": str(e)},
                ))
        
        await session.send_tool_response(function_responses=function_responses)
        
        # Small delay to prevent race conditions
        await asyncio.sleep(0.05)
        # await session.send_client_event(event_type="turn_complete")
    async def run(self):
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                if self.video_mode == "camera":
                    tg.create_task(self.get_frames())
                elif self.video_mode == "screen":
                    tg.create_task(self.get_screen())

                tg.create_task(self.receive_audio(tg,session))
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
        except ExceptionGroup as EG:
            self.audio_stream.close()
            traceback.print_exception(EG)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="pixels to stream from",
        choices=["camera", "screen", "none"],
    )
    args = parser.parse_args()
    main = AudioLoop(video_mode=args.mode)
    asyncio.run(main.run())