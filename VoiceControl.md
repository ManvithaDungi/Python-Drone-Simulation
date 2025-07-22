## Method 2.2: AI-Enhanced Voice Control with Google Gemini 2.5 Flash

This advanced script provides intelligent, natural language drone control using Google's Gemini 2.5 Flash model for command interpretation. The system can understand conversational speech and distinguish between drone commands and general conversation.

### Prerequisites

#### Step 1: Install Dependencies
```bash
# Audio processing dependencies
sudo apt install portaudio19-dev python3-pyaudio

# Python packages
pip install SpeechRecognition
pip install PyAudio
pip install mavsdk
pip install google-genai
```

#### Step 2: Get Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create or sign in to your account
3. Generate a new API key
4. Set it as an environment variable (recommended):
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Installation and Setup

#### Step 1: Download the Enhanced Script
Save the AI-enhanced voice control script as `ai_voice_control.py`

#### Step 2: Set Up API Key
You can provide your Gemini API key in two ways:

**Option A: Environment Variable (Recommended)**
```bash
export GEMINI_API_KEY="your_api_key_here"
python3 ai_voice_control.py
```

**Option B: Enter During Runtime**
The script will prompt you for the API key when you run it.

#### Step 3: Run the Script
Ensure PX4 SITL is running:
```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500_depth
```

In another terminal, run the enhanced script:
```bash
python3 ai_voice_control.py
```

### Available Control Modes

The script offers multiple control options through an interactive menu:

1. **Arm** - Arm the drone motors
2. **Take off** - Automated takeoff to specified altitude
3. **Manual control** - Keyboard-based distance and turning control
4. **Return to launch** - Automated return to starting position
5. **Land** - Automated landing
6. **Exit** - Safely stop and exit
7. **AI-Enhanced Voice Control** - Natural language voice commands

### Voice Command Examples

#### Natural Language Commands
The AI can understand various ways of expressing commands:

**Movement Commands:**
- "Move forward 3 meters"
- "Go ahead a little bit"
- "Fly backward 5 meters"
- "Slide to the right 2 meters"
- "Go up 4 meters"
- "Come down slowly"

**Rotation Commands:**
- "Turn right 45 degrees"
- "Turn left 90 degrees"
- "Spin around" (180 degrees)
- "Face the other direction"

**Action Commands:**
- "Land the drone"
- "Take off to 3 meters"
- "Return home"
- "Return to launch"
- "Stop right there"
- "Hover in place"

**Control Commands:**
- "Exit voice control"
- "Quit the program"
- "End session"

#### Conversational Intelligence
The system will ignore non-drone related speech:
- "How's the weather today?" → Ignored
- "I think the battery is low" → Ignored
- "What time is it?" → Ignored

But will respond to implied commands:
- "I think we should go forward" → Executes forward movement
- "Maybe try going up a bit" → Executes upward movement

### Technical Details

#### LLM Integration
- **Model**: Google Gemini 2.5 Flash
- **Processing**: JSON-structured command interpretation
- **Fallback**: Keyword-based parsing if LLM fails
- **Response Time**: Optimized with thinking budget set to 0

#### Movement Parameters
- **Default Speed**: Adaptive based on distance (0.5-3.0 m/s)
- **Default Distance**: 2.0 meters if not specified
- **Default Turn Angle**: 90 degrees if not specified
- **Turn Speed**: 30 degrees per second

#### Safety Features
- **Confidence Scoring**: Commands include confidence ratings
- **Fallback Processing**: Basic keyword matching as backup
- **Error Handling**: Graceful handling of API failures
- **Command Validation**: JSON validation for LLM responses

### Troubleshooting

#### Common Issues

**API Key Issues:**
```bash
# Check if environment variable is set
echo $GEMINI_API_KEY

# Set temporarily for current session
export GEMINI_API_KEY="your_key_here"
```

**Audio Issues:**
```bash
# Test microphone
arecord -l

# Reinstall audio dependencies
sudo apt reinstall portaudio19-dev python3-pyaudio
pip install --force-reinstall PyAudio
```

**LLM Connection Issues:**
- Verify API key is valid
- Check internet connection
- Script will fall back to basic voice control if LLM fails

**PX4 Connection Issues:**
```bash
# Ensure PX4 SITL is running
ps aux | grep px4

# Restart if needed
cd ~/PX4-Autopilot
make px4_sitl gz_x500_depth
```

### Usage Tips

1. **Speak Clearly**: Ensure good microphone quality and minimal background noise
2. **Natural Speech**: Use conversational language - the AI understands context
3. **Specify Distances**: Include specific distances for more precise control
4. **Wait for Processing**: Allow time for speech recognition and LLM processing
5. **Use Fallback**: If AI fails, the script includes manual and basic voice control

### Example Session Flow

```
$ python3 ai_voice_control.py
🤖 Setting up Google Gemini 2.5 Flash integration...
[✔] Found GEMINI_API_KEY environment variable
[✔] Google Gemini 2.5 Flash processor initialized successfully!
[✔] Connected to drone.

Choose an option:
1) Arm
2) Take off  
3) Manual control
4) Return to launch
5) Land
6) Exit
7) Enhanced Voice Control (with Gemini 2.5 Flash)

Enter choice: 7

🎙️ Enhanced Voice Control Active
💡 I can understand natural language! Try saying:
   - 'Move forward 3 meters'
   - 'Turn left 45 degrees'
   - 'Go up a little bit'
   - 'Land the drone'

🎤 Listening... (speak naturally)
[🎧] You said: 'move forward 3 meters'
[🧠] LLM Interpretation: Moving forward 3.0 meters
[🚁] Moving FORWARD 3.0m at 2.0m/s
```

This AI-enhanced voice control provides the most intuitive and flexible way to control your PX4 drone simulation, making it accessible to users who prefer natural language interaction over technical commands.