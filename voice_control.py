#!/usr/bin/env python3

import asyncio
import math
import json
import os
from google import genai
import speech_recognition as sr
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw
from typing import Dict, Optional, Tuple


# ---------- LLM INTEGRATION ----------

class DroneCommandProcessor:
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the LLM command processor
        Args:
            api_key: Your Google Gemini API key (or set GEMINI_API_KEY env var)
            model: Model to use (gemini-2.5-flash, gemini-1.5-pro, etc.)
        """
        # Set API key as environment variable if provided
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
        
        # Initialize the new Gemini client
        self.client = genai.Client()
        self.model_name = model
        
        # System prompt to define the LLM's role
        self.system_prompt = """
You are a drone command interpreter. Your job is to analyze speech input and determine if it contains drone control commands.

Available drone commands:
- Movement: forward, backward, left, right, up, down (with optional distance in meters)
- Rotation: turn left, turn right (with degrees), turn around/back
- Actions: takeoff, land, return home, arm, disarm
- Control: stop, hover, exit

Return a JSON response with:
{
    "is_drone_command": boolean,
    "command_type": "movement" | "rotation" | "action" | "control" | null,
    "action": specific action name or null,
    "parameters": {
        "direction": string or null,
        "distance": number or null (in meters, default 2.0),
        "angle": number or null (in degrees, default 90)
    },
    "confidence": float (0.0 to 1.0),
    "original_text": the input text,
    "interpretation": human readable explanation
}

Examples:
- "move forward 3 meters" → is_drone_command: true, action: "forward", distance: 3.0
- "turn right 45 degrees" → is_drone_command: true, action: "turn_right", angle: 45
- "how's the weather today?" → is_drone_command: false
- "land the drone" → is_drone_command: true, action: "land"
- "I think we should go forward" → is_drone_command: true, action: "forward", distance: 2.0
- "stop" → is_drone_command: true, action: "stop"

Be flexible with natural language - people might say "go ahead", "move up a bit", "spin around", etc.
"""

    async def process_speech(self, speech_text: str) -> Dict:
        """Process speech text and return command interpretation"""
        try:
            prompt = f"""{self.system_prompt}

Analyze this speech: '{speech_text}'

Respond with valid JSON only:"""
            
            # Use the new client API with thinking budget set to 0 for faster responses
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent responses
                    max_output_tokens=300,
                    system_instruction=None,
                    thinking_budget=0  # Disable thinking for faster responses
                )
            )
            
            # Clean the response text and parse JSON
            response_text = response.text.strip()
            
            # Remove any markdown code block formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"[!] Gemini returned invalid JSON: {e}")
            print(f"[!] Raw response: {response.text}")
            return self._fallback_processing(speech_text)
        except Exception as e:
            print(f"[!] Gemini API error: {e}")
            return self._fallback_processing(speech_text)
    
    def _fallback_processing(self, speech_text: str) -> Dict:
        """Simple keyword-based fallback if LLM fails"""
        speech = speech_text.lower()
        
        # Basic keyword matching as fallback
        if any(word in speech for word in ["forward", "ahead", "front"]):
            return {"is_drone_command": True, "action": "forward", "parameters": {"distance": 2.0}}
        elif any(word in speech for word in ["back", "backward", "reverse"]):
            return {"is_drone_command": True, "action": "backward", "parameters": {"distance": 2.0}}
        elif any(word in speech for word in ["left"]) and "turn" not in speech:
            return {"is_drone_command": True, "action": "left", "parameters": {"distance": 2.0}}
        elif any(word in speech for word in ["right"]) and "turn" not in speech:
            return {"is_drone_command": True, "action": "right", "parameters": {"distance": 2.0}}
        elif any(word in speech for word in ["up", "rise", "ascend"]):
            return {"is_drone_command": True, "action": "up", "parameters": {"distance": 2.0}}
        elif any(word in speech for word in ["down", "descend", "lower"]):
            return {"is_drone_command": True, "action": "down", "parameters": {"distance": 2.0}}
        elif "turn right" in speech:
            return {"is_drone_command": True, "action": "turn_right", "parameters": {"angle": 90}}
        elif "turn left" in speech:
            return {"is_drone_command": True, "action": "turn_left", "parameters": {"angle": 90}}
        elif any(word in speech for word in ["land", "landing"]):
            return {"is_drone_command": True, "action": "land", "parameters": {}}
        elif any(word in speech for word in ["takeoff", "take off", "launch"]):
            return {"is_drone_command": True, "action": "takeoff", "parameters": {}}
        elif any(word in speech for word in ["home", "return", "rth"]):
            return {"is_drone_command": True, "action": "return_home", "parameters": {}}
        elif any(word in speech for word in ["stop", "halt", "hover"]):
            return {"is_drone_command": True, "action": "stop", "parameters": {}}
        elif any(word in speech for word in ["exit", "quit", "end"]):
            return {"is_drone_command": True, "action": "exit", "parameters": {}}
        else:
            return {"is_drone_command": False, "interpretation": "Not a drone command"}


# ---------- TELEMETRY HELPERS ----------

async def debug_telemetry(drone):
    async for pos in drone.telemetry.position():
        print(f"[DEBUG] PX4 says: ALT = {pos.relative_altitude_m:.3f} m")
        break
    async for is_air in drone.telemetry.in_air():
        print(f"[DEBUG] PX4 in_air = {is_air}")
        break
    async for is_armed in drone.telemetry.armed():
        print(f"[DEBUG] PX4 armed = {is_armed}")
        break


# ---------- BASIC ACTIONS ----------

async def connect():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("Connecting...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("[✔] Connected to drone.")
            break
    return drone

async def arm(drone):
    print("Arming...")
    await drone.action.arm()
    await asyncio.sleep(2)

async def takeoff(drone, alt=2.0):
    print(f"[↑] Taking off to {alt} meters using offboard control...")
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    try:
        await drone.offboard.start()
    except Exception as e:
        print(f"[x] Could not start Offboard mode for takeoff: {e}")
        return

    ascent_speed = -1.0  # m/s upward
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, ascent_speed, 0.0))
    await asyncio.sleep(alt / abs(ascent_speed))
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))

async def land(drone):
    print("Landing...")
    await drone.action.land()
    await asyncio.sleep(5)

async def return_to_launch(drone):
    print("Returning to launch...")
    await drone.action.return_to_launch()
    await asyncio.sleep(5)


# ---------- ENHANCED VOICE CONTROL WITH LLM ----------

async def enhanced_voice_control(drone, llm_processor: DroneCommandProcessor):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n🎙️ Enhanced Voice Control Active")
    print("💡 I can understand natural language! Try saying:")
    print("   - 'Move forward 3 meters'")
    print("   - 'Turn left 45 degrees'") 
    print("   - 'Go up a little bit'")
    print("   - 'Land the drone'")
    print("   - 'How's the weather?' (I'll ignore non-commands)")

    DEFAULT_SPEED = 2.0  # m/s
    TURN_SPEED = 30  # deg/sec
    yaw_heading = 0.0

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
    try:
        await drone.offboard.start()
    except Exception as e:
        print(f"[x] Could not start Offboard mode: {e}")
        return

    while True:
        with mic as source:
            print("\n🎤 Listening... (speak naturally)")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        try:
            speech = recognizer.recognize_google(audio)
            print(f"[🎧] You said: '{speech}'")

            # Process speech with LLM
            command_result = await llm_processor.process_speech(speech)
            
            if not command_result["is_drone_command"]:
                print(f"[💬] That sounds like general conversation: {command_result.get('interpretation', 'Not a drone command')}")
                print("     I'm only responding to drone commands right now.")
                continue
                
            print(f"[🧠] LLM Interpretation: {command_result.get('interpretation', 'Drone command detected')}")
            
            action = command_result.get("action")
            params = command_result.get("parameters", {})
            
            if action == "exit":
                print("[👋] Voice control ending...")
                await drone.offboard.stop()
                break
                
            elif action == "land":
                await drone.offboard.stop()
                await land(drone)
                break
                
            elif action == "return_home":
                await drone.offboard.stop()
                await return_to_launch(drone)
                break
                
            elif action == "takeoff":
                alt = params.get("distance", 2.0)
                await drone.offboard.stop()
                await takeoff(drone, alt)
                await drone.offboard.start()
                
            elif action == "stop":
                print("[⏸️] Stopping and hovering...")
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                
            elif action in ["turn_right", "turn_left"]:
                angle = params.get("angle", 90)
                if action == "turn_right":
                    yaw_heading += angle
                    print(f"[↻] Turning right {angle}°")
                else:
                    yaw_heading -= angle
                    print(f"[↺] Turning left {angle}°")
                    
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                await asyncio.sleep(angle / TURN_SPEED)
                
            elif action in ["forward", "backward", "left", "right", "up", "down"]:
                distance = params.get("distance", 2.0)
                speed = min(3.0, max(0.5, distance / 1.5))  # Adaptive speed
                duration = distance / speed
                
                vel_map = {
                    "forward": VelocityNedYaw(speed, 0.0, 0.0, yaw_heading),
                    "backward": VelocityNedYaw(-speed, 0.0, 0.0, yaw_heading),
                    "right": VelocityNedYaw(0.0, speed, 0.0, yaw_heading),
                    "left": VelocityNedYaw(0.0, -speed, 0.0, yaw_heading),
                    "up": VelocityNedYaw(0.0, 0.0, -speed, yaw_heading),
                    "down": VelocityNedYaw(0.0, 0.0, speed, yaw_heading),
                }
                
                vel = vel_map[action]
                print(f"[🚁] Moving {action.upper()} {distance}m at {speed:.1f}m/s")
                
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(duration)
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                
            else:
                print(f"[?] Unknown action: {action}")

        except sr.WaitTimeoutError:
            print("[⏰] No speech detected, still listening...")
        except sr.UnknownValueError:
            print("[❓] Could not understand what you said, please try again.")
        except Exception as e:
            print(f"[❌] Error: {e}")


# ---------- MANUAL CONTROL (UNCHANGED) ----------

async def manual_control(drone):
    print("Manual control:")
    print("→ Movement: 'f 1', 'r 1', 'u 1', 'd 1'")
    print("→ Turning: 'turn_r 90', 'turn_l 45', 'turn_b'")
    print("→ Commands: land, rth, debug, exit")

    MAX_SPEED = 2.0
    MIN_SPEED = 0.2
    TIME_GOAL = 1.5
    TURN_SPEED = 30  # deg/sec

    yaw_heading = 0.0

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
    try:
        await drone.offboard.start()
    except Exception as e:
        print(f"[x] Could not start Offboard mode: {e}")
        return

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "exit":
            await drone.offboard.stop()
            break
        elif cmd == "land":
            await drone.offboard.stop()
            await land(drone)
            break
        elif cmd == "rth":
            await drone.offboard.stop()
            await return_to_launch(drone)
            break
        elif cmd == "debug":
            await debug_telemetry(drone)
        elif cmd.startswith("turn_r"):
            try:
                _, deg = cmd.split()
                deg = float(deg)
                yaw_heading += deg
                print(f"↻ Turning right {deg}°, new heading: {yaw_heading}°")
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                await asyncio.sleep(deg / TURN_SPEED)
            except:
                print("[x] Format: turn_r <angle>")
        elif cmd.startswith("turn_l"):
            try:
                _, deg = cmd.split()
                deg = float(deg)
                yaw_heading -= deg
                print(f"↺ Turning left {deg}°, new heading: {yaw_heading}°")
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                await asyncio.sleep(deg / TURN_SPEED)
            except:
                print("[x] Format: turn_l <angle>")
        elif cmd == "turn_b":
            yaw_heading += 180
            print(f"↻ Turning back (180°), new heading: {yaw_heading}°")
            await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
            await asyncio.sleep(180 / TURN_SPEED)
        else:
            try:
                direction, distance = cmd.split()
                distance = max(0.1, min(5.0, float(distance)))
                speed = min(MAX_SPEED, max(MIN_SPEED, distance / TIME_GOAL))
                duration = distance / speed

                if direction == "f":
                    vel = VelocityNedYaw(speed, 0.0, 0.0, yaw_heading)
                elif direction == "b":
                    vel = VelocityNedYaw(-speed, 0.0, 0.0, yaw_heading)
                elif direction == "r":
                    vel = VelocityNedYaw(0.0, speed, 0.0, yaw_heading)
                elif direction == "l":
                    vel = VelocityNedYaw(0.0, -speed, 0.0, yaw_heading)
                elif direction == "u":
                    vel = VelocityNedYaw(0.0, 0.0, -speed, yaw_heading)
                elif direction == "d":
                    vel = VelocityNedYaw(0.0, 0.0, speed, yaw_heading)
                else:
                    print("[x] Unknown direction.")
                    continue

                print(f"[→] Moving {direction.upper()} {distance}m at {speed:.2f} m/s for {duration:.2f}s | Yaw: {yaw_heading}°")
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(duration)
                await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
            except Exception as e:
                print(f"[x] Error: {e}")


# ---------- MENU ----------

async def menu():
    # Initialize LLM processor
    print("🤖 Setting up Google Gemini 2.5 Flash integration...")
    
    # Check if API key is already set as environment variable
    api_key_from_env = os.environ.get('GEMINI_API_KEY')
    
    if api_key_from_env:
        print("[✔] Found GEMINI_API_KEY environment variable")
        API_KEY = api_key_from_env
    else:
        API_KEY = input("Enter your Google Gemini API key (or press Enter to use basic voice control): ").strip()
    
    if API_KEY:
        try:
            llm_processor = DroneCommandProcessor(API_KEY)
            print("[✔] Google Gemini 2.5 Flash processor initialized successfully!")
        except Exception as e:
            print(f"[!] Failed to initialize Gemini: {e}")
            print("    Falling back to basic voice control...")
            llm_processor = None
    else:
        llm_processor = None
    
    drone = await connect()

    while True:
        print("\nChoose an option:")
        print("1) Arm")
        print("2) Take off")
        print("3) Manual control (distance + turning)")
        print("4) Return to launch")
        print("5) Land")
        print("6) Exit")
        if llm_processor:
            print("7) Enhanced Voice Control (with Gemini 2.5 Flash)")
        else:
            print("7) Basic Voice Control")

        choice = input("Enter choice: ")

        try:
            if choice == "1":
                await arm(drone)
            elif choice == "2":
                await takeoff(drone)
            elif choice == "3":
                await manual_control(drone)
            elif choice == "4":
                await return_to_launch(drone)
            elif choice == "5":
                await land(drone)
            elif choice == "6":
                print("Exiting and stopping offboard if active.")
                try:
                    await drone.offboard.stop()
                except:
                    pass
                break
            elif choice == "7":
                if llm_processor:
                    await enhanced_voice_control(drone, llm_processor)
                else:
                    # Fallback to your original voice control
                    await voice_control_basic(drone)
            else:
                print("[x] Invalid option.")
        except Exception as e:
            print(f"[x] Error: {e}")

    print("[✔] Session ended.")


# ---------- BASIC VOICE CONTROL (FALLBACK) ----------

async def voice_control_basic(drone):
    """Original voice control as fallback"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n🎙️ Basic Voice Control Active")
    print("Say things like: 'forward', 'turn right 90', 'land', 'exit'")

    FIXED_DIST = 5.0  # meters
    SPEED = 2.0  # m/s
    yaw_heading = 0.0

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
    try:
        await drone.offboard.start()
    except Exception as e:
        print(f"[x] Could not start Offboard mode: {e}")
        return

    while True:
        with mic as source:
            print("\nListening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            speech = recognizer.recognize_google(audio).lower()
            print(f"[🎧] You said: {speech}")

            if "exit" in speech:
                await drone.offboard.stop()
                break
            elif "land" in speech:
                await drone.offboard.stop()
                await land(drone)
                break
            elif "return" in speech or "home" in speech:
                await drone.offboard.stop()
                await return_to_launch(drone)
                break
            elif "turn right" in speech:
                try:
                    deg = int(speech.split("right")[-1].strip())
                    yaw_heading += deg
                    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                    await asyncio.sleep(deg / 30)
                except:
                    print("[x] Say: turn right <degrees>")
            elif "turn left" in speech:
                try:
                    deg = int(speech.split("left")[-1].strip())
                    yaw_heading -= deg
                    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))
                    await asyncio.sleep(deg / 30)
                except:
                    print("[x] Say: turn left <degrees>")
            elif "forward" in speech:
                vel = VelocityNedYaw(SPEED, 0.0, 0.0, yaw_heading)
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(FIXED_DIST / SPEED)
            elif "back" in speech:
                vel = VelocityNedYaw(-SPEED, 0.0, 0.0, yaw_heading)
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(FIXED_DIST / SPEED)
            elif "right" in speech and "turn" not in speech:
                vel = VelocityNedYaw(0.0, SPEED, 0.0, yaw_heading)
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(FIXED_DIST / SPEED)
            elif "left" in speech and "turn" not in speech:
                vel = VelocityNedYaw(0.0, -SPEED, 0.0, yaw_heading)
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(FIXED_DIST / SPEED)
            elif "up" in speech:
                vel = VelocityNedYaw(0.0, 0.0, -SPEED, yaw_heading)
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(FIXED_DIST / SPEED)
            elif "down" in speech:
                vel = VelocityNedYaw(0.0, 0.0, SPEED, yaw_heading)
                await drone.offboard.set_velocity_ned(vel)
                await asyncio.sleep(FIXED_DIST / SPEED)
            else:
                print("[x] Unrecognized command.")

            # Always stop after each move
            await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_heading))

        except sr.UnknownValueError:
            print("[x] Could not understand audio.")
        except Exception as e:
            print(f"[x] Error: {e}")


if __name__ == "__main__":
    asyncio.run(menu())
