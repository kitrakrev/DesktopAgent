# 🎤 Voice-Controlled Computer Assistant (test3.py)

An AI-powered voice assistant that controls your computer through natural language commands using Google's Gemini 2.5 Flash with Live API.

---

## ✨ Features

### 🖱️ **Mouse Control**
- Move mouse to specific coordinates (absolute or relative)
- Click (left/right, single/double/triple)
- Hold and release mouse buttons
- Smooth animated mouse movements
- Scroll in any direction
- AI-powered coordinate detection from screen descriptions

### ⌨️ **Keyboard Control**
- Press individual keys (including special keys)
- Type text with optional select-all-first
- Execute keyboard shortcuts (Cmd+C, Cmd+V, etc.)
- Replace text in fields

### 🎯 **AI-Powered Screen Understanding**
- **Smart Coordinate Detection**: Tell the AI "click on Discord" and it finds it!
- **Quiz Generator**: Generates fun quizzes based on what's on your screen
- **Visual Recognition**: Analyzes screen content with Gemini 2.5 Pro

### 🎨 **User Interface**
- Real-time voice interaction with audio feedback
- Translucent modal windows for quiz display
- Screen sharing with cursor overlay
- Visual grid system for precise coordinate detection

---

## 📋 Prerequisites

### System Requirements
- **OS**: macOS (tested on macOS 14+)
- **Python**: 3.12 or higher
- **Microphone & Speakers**: Required for voice interaction
- **Screen Recording Permission**: For screen capture
- **Accessibility Permission**: For mouse/keyboard control

### API Key
- Google AI API Key from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## 🚀 Installation

### 1. Install Dependencies

Using `uv` (recommended):
```bash
cd voice-chat
uv pip install python-dotenv google-genai pyaudio pillow opencv-python mss pynput pyautogui numpy
```

Or using pip:
```bash
pip install python-dotenv google-genai pyaudio pillow opencv-python mss pynput pyautogui numpy
```

### 2. Set Up Environment

Create a `.env` file in the `voice-chat` directory:
```bash
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

Or export it in your shell:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### 3. Grant macOS Permissions

#### Accessibility Permission (Required for mouse/keyboard control)
1. Open **System Settings**
2. Go to **Privacy & Security** → **Accessibility**
3. Click the **+** button
4. Add **Terminal** (or your IDE like VS Code, PyCharm)
5. Enable the checkbox
6. Restart Terminal

#### Screen Recording Permission (Required for screen capture)
1. Open **System Settings**
2. Go to **Privacy & Security** → **Screen Recording**
3. Enable **Terminal** (or your IDE)
4. Restart Terminal

### 4. Test Permissions

Run the permission test script:
```bash
uv run python test_permissions.py
```

Expected output:
```
✅ Mouse controller created
✅ Mouse moved successfully!
✅ Accessibility permission is WORKING
✅ Screen captured successfully!
✅ Screen Recording permission is WORKING
🎉 ALL PERMISSIONS ARE WORKING!
```

---

## 🎮 Usage

### Running the Application

**Screen Share Mode** (recommended):
```bash
uv run python test3.py --mode screen
```

**Camera Mode**:
```bash
uv run python test3.py --mode camera
```

**Audio Only** (no video):
```bash
uv run python test3.py --mode none
```

### Voice Commands Examples

#### Mouse Control
- "Move the mouse to the center of the screen"
- "Click on Discord" *(AI finds and clicks Discord icon)*
- "Double click here"
- "Right click on the file"
- "Scroll down"
- "Move mouse 100 pixels to the right"

#### Keyboard & Text
- "Type hello world"
- "Press enter"
- "Copy this" *(Cmd+C)*
- "Paste it" *(Cmd+V)*
- "Select all and replace with: new text here"
- "Press command shift S" *(Save As)*

#### Screen Understanding
- "What's on my screen?"
- "Click the close button"
- "Find the search box"
- "Generate a quiz from my screen"

#### Fun Features
- "Show me a quiz" *(Generates interactive quiz from screen)*
- "Create quiz questions"

### Text Input Mode

Type commands when not speaking:
```
message > [Type your command here]
```

Type `q` to quit.

---

## 🛠️ Available Tools

### Mouse Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `move_mouse_absolute` | Move to exact coordinates | x, y |
| `move_mouse_relative` | Move relative to current position | x, y |
| `left_click_mouse` | Left click | count (default: 1) |
| `right_click_mouse` | Right click | count (default: 1) |
| `hold_left_mouse_button` | Press and hold left button | - |
| `release_left_mouse_button` | Release left button | - |
| `hold_right_mouse_button` | Press and hold right button | - |
| `release_right_mouse_button` | Release right button | - |
| `scroll_mouse_by` | Scroll | dx, dy |
| `get_mouse_position` | Get current position | - |

### Keyboard Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `press_key` | Press single key | key |
| `type_text` | Type text | text, select_all_first |
| `select_all_and_replace` | Replace all text | text |
| `press_key_combination` | Keyboard shortcuts | keys (array) |

**Special Keys**: space, enter, shift, ctrl, alt, cmd, tab, esc, up, down, left, right, backspace, delete

### Screen Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `smart_detect_screen_coordinates` | AI finds UI element | prompt |
| `generate_quiz_from_screen` | Create interactive quiz | - |
| `get_screen_size` | Get screen dimensions | - |

---

## 🎯 How It Works

### AI Workflow for Clicking Elements

When you say "Click on Discord", the AI follows this sequence:

1. **Detect**: Calls `smart_detect_screen_coordinates("Discord")`
   - Captures screen with grid overlay
   - Sends to Gemini 2.5 Pro
   - Gets coordinates: `x=250, y=575`

2. **Move**: Calls `move_mouse_absolute(250, 575)`
   - Smoothly moves mouse in 20 steps
   - 5ms delay between steps for smooth animation

3. **Click**: Calls `left_click_mouse()`
   - Clicks at the current position

4. **Respond**: AI confirms verbally: "I've clicked on Discord"

### Quiz Generation

When you say "Generate a quiz":

1. **Capture**: Takes screenshot of current screen
2. **Analyze**: Sends to Gemini 2.5 Pro with prompt
3. **Generate**: Creates 3 questions:
   - 2 about visible content
   - 1 fun/creative question
4. **Display**: Shows in translucent modal window
   - 95% opacity
   - Always on top
   - Press ESC or click button to close

---

## 🔧 Configuration

### Model Settings
```python
MODEL = "gemini-2.5-flash-native-audio-preview-09-2025"
```

### Audio Settings
```python
SEND_SAMPLE_RATE = 16000    # Input: 16kHz
RECEIVE_SAMPLE_RATE = 24000 # Output: 24kHz
CHUNK_SIZE = 1024           # Audio buffer size
```

### System Instruction
The AI follows a strict workflow to ensure reliable operation:
- Always detect coordinates before clicking
- Never guess coordinates
- Move mouse before clicking
- Confirm actions verbally
- Break complex tasks into steps

---

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│         User Voice Input (Microphone)       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     Gemini 2.5 Flash Live API (WebSocket)   │
│  • Speech-to-text                           │
│  • Natural language understanding           │
│  • Tool/function calling                    │
│  • Text-to-speech                           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│            Tool Execution Layer             │
│  • Mouse control (pynput)                   │
│  • Keyboard control (pynput)                │
│  • Screen capture (mss)                     │
│  • Vision AI (Gemini 2.5 Pro)              │
│  • GUI (tkinter)                            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│       macOS System (with permissions)       │
│  • Mouse/keyboard events                    │
│  • Screen capture                           │
│  • Audio I/O                                │
└─────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Voice Not Responding

**Symptom**: Tools execute but AI doesn't speak back

**Fix**: Check line 951 in test3.py:
```python
await asyncio.sleep(0.05)  # This must be uncommented!
```

### Mouse Not Moving

**Symptoms**: 
- Clicks happen but mouse doesn't move
- Commands detected but no action

**Fixes**:
1. **Check Accessibility Permission**:
   ```bash
   uv run python test_permissions.py
   ```

2. **Verify global mouse controller** (line 81):
   ```python
   _MOUSE_CONTROLLER = mouse.Controller()
   ```

3. **Ensure functions use global controller**:
   ```python
   # Correct ✅
   _MOUSE_CONTROLLER.click(mouse.Button.left, count)
   
   # Wrong ❌
   mouse.Controller().click(mouse.Button.left, count)
   ```

### Screen Capture Failed

**Error**: `CoreGraphics.CGWindowListCreateImage() failed`

**Fix**: Grant Screen Recording permission (see Installation step 3)

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'pynput'`

**Fix**: 
```bash
# Run with uv
uv run python test3.py --mode screen

# Or install dependencies
uv pip install pynput pyautogui mss opencv-python
```

### Quiz Modal Not Appearing

**Cause**: Tkinter requires main thread on macOS

**Current Behavior**: Quiz prints to console if not on main thread (this is safe)

### Audio Echo/Feedback

**Solution**: **Use headphones!** The script doesn't have echo cancellation.

---

## 🔒 Security & Privacy

### Permissions Required
- **Accessibility**: Controls mouse/keyboard
- **Screen Recording**: Captures screen content
- **Microphone**: Records voice commands
- **Internet**: Sends audio/video to Google AI

### Data Sent to Google
- Voice audio (for speech recognition)
- Screen images (for coordinate detection and quiz generation)
- Text transcripts

### Local Data
- Screenshots saved in `screens_*` folders
- Quiz screenshots in `quiz_screens_*` folders
- Audio frames processed in memory (not saved)

---

## 📝 Tips & Best Practices

1. **Use Headphones**: Prevent audio feedback loops
2. **Speak Clearly**: Better recognition accuracy
3. **Be Specific**: "Click on Discord" works better than "click there"
4. **Break Down Tasks**: Complex tasks work better in steps
5. **Check Permissions**: Run test script if things stop working
6. **Monitor Console**: Watch for tool execution logs
7. **Use Screen Mode**: Better for UI interaction than camera mode

---

## 🎓 Example Workflows

### Open an Application
```
You: "Click on Chrome"
AI: [Detects coordinates]
AI: [Moves mouse]
AI: [Clicks]
AI: "I've clicked on Chrome for you"
```

### Copy and Paste
```
You: "Select all this text"
AI: [Presses Cmd+A]
You: "Copy it"
AI: [Presses Cmd+C]
You: "Now paste it in the search box"
AI: [Finds search box, clicks, presses Cmd+V]
```

### Fill a Form
```
You: "Type my email address"
AI: [Types text]
You: "Press tab"
AI: [Moves to next field]
You: "Type my password"
AI: [Types text]
You: "Press enter"
AI: [Submits form]
```

---

## 📚 Related Files

- `test_permissions.py` - Test macOS permissions
- `test2.py` - Earlier version (basic features)
- `BUGFIX_SUMMARY.md` - List of bugs fixed
- `CRITICAL_FIXES.md` - Technical details of fixes
- `NEW_FEATURES_SUMMARY.md` - New features added

---

## 🤝 Contributing

To add new tools:

1. **Define the function**:
```python
def my_new_tool(param1: str, param2: int):
    """Description of what the tool does."""
    # Implementation
    return {"result": "success"}
```

2. **Add to func_names_dict**:
```python
func_names_dict = {
    # ... existing tools
    "my_new_tool": my_new_tool,
}
```

3. **Add to tools declaration**:
```python
types.FunctionDeclaration(
    name="my_new_tool",
    description="What the AI needs to know about this tool",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "param1": types.Schema(type=types.Type.STRING),
            "param2": types.Schema(type=types.Type.NUMBER)
        }
    )
),
```

---

## 📄 License

Part of the GEMINI_HACK project.

---

## 🙏 Acknowledgments

- Google Gemini 2.5 Flash Live API
- Google Gemini 2.5 Pro Vision API
- pynput for cross-platform input control
- mss for fast screen capture
- PyAudio for audio streaming

---

## 📞 Support

**Issues?** Check troubleshooting section above or run:
```bash
uv run python test_permissions.py
```

**Status**: ✅ All features tested and working on macOS  
**Version**: 1.0  
**Last Updated**: October 19, 2025

