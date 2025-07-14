# Python-Drone-Simulation
This is the full setup and complete process of PX4 Autopilot with Gazebo Ignition Harmonic and QGroundControl, including integration with Python using MAVSDK.

## Prerequisites :
- Ubuntu 22.04/24.04
- Gazebo Harmonic
- PX4 and its Dependencies
- QGroundControl

## Setting up Gazebo :
 We are using Gazebo Harmonic, you can also use Gazebo Ignition.
 
 ### Step 1: Set up the Gazebo APT repository
```
sudo apt update
sudo apt install curl gnupg lsb-release
```
Add the OSRF key and repository:
```
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.osrfoundation.org/gazebo.key | sudo gpg --dearmor -o /etc/apt/keyrings/gazebo.gpg
```

Add the repository:
```
echo "deb [signed-by=/etc/apt/keyrings/gazebo.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
```
### Step 2: Install Gazebo harmonic
```
sudo apt update
sudo apt install gz-harmonic
```
You can also install development tools if needed:
```
sudo apt install gz-harmonic-dev
```
### Step 3: Verify Installation
Run
```
gz sim --version
```
Expected Output : Something like this
```
Gazebo Sim, version 8.X.X
Copyright (C) 2018 Open Source Robotics Foundation.XXXXXXXX
Released under the Apache 2.0 License.XXXXX
```
### Step 4: Run a sample
You should see the GUI open when you run this.
```
gz sim shapes.sdf
```
References  : https://gazebosim.org/docs/harmonic/install

## Setting up QGroundControl :
Download QGroundControl from https://qgroundcontrol.com/

## Cloning PX4-Autopilot :

### Step 1: Clone PX4 Autopilot from git
```
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
```
### Step 2: Install PX4-Dependencies
```
bash ./Tools/setup/ubuntu.sh
```
### Step 3: Build PX4 for Ignition
make sure you are in PX4-Autopilot folder while running this
```
PX4_SIM_MODEL=x500 PX4_GZ_VERSION=harmonic make px4_sitl gz
```
### Step 4 : Connecting to QGroundControl
Make it executalble and run
```
chmod +x ./QGroundControl.AppImage
./QGroundControl.AppImage
```

## Python OffBoard Control with MAVSDK:

### Step 1: Install MAVSDK for python:
```
pip install mavsdk
```
### Step 2 : Run a Control Script :
Create a file offboard_control.py and run
```
python3 offboard_control.py
```
Make sure PX4 SITL is running before this

## Adding Camera and Custom Worlds :
To attach a virtual camera, edit the drone’s .sdf file inside PX4-Autopilot/Tools/simulation/gz/models/

To import a custom world:
```
export PX4_GZ_WORLD=your_world_name
PX4_SIM_MODEL=x500 PX4_GZ_VERSION=harmonic make px4_sitl gz
```
References

    PX4 Docs: https://docs.px4.io/

    Gazebo Harmonic Docs: https://gazebosim.org/docs/harmonic

    MAVSDK Python: https://mavsdk.mavlink.io/main/en/
    
## Setting up ROS2 :
