#!/usr/bin/env python3

import asyncio
import math
import speech_recognition as sr
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw


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


# ---------- MANUAL CONTROL WITH DISTANCE + YAW ----------

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


# ---------- VOICE CONTROL ----------

async def voice_control(drone):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n🎙️ Voice Control Active")
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



# ---------- MENU ----------

async def menu():
    drone = await connect()

    while True:
        print("\nChoose an option:")
        print("1) Arm")
        print("2) Take off")
        print("3) Manual control (distance + turning)")
        print("4) Return to launch")
        print("5) Land")
        print("6) Exit")
        print("7) Voice control")

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
                await voice_control(drone)
            else:
                print("[x] Invalid option.")
        except Exception as e:
            print(f"[x] Error: {e}")

    print("[✔] Session ended.")


if __name__ == "__main__":
    asyncio.run(menu())

