# Python Drone Simulation with PX4 Autopilot

This comprehensive guide covers the complete setup process for PX4 Autopilot with Gazebo simulation and various control methods including QGroundControl, Python MAVSDK, and ROS2 integration.

## Overview

This simulation setup allows you to control drones in a virtual Gazebo environment using PX4 Autopilot with three different control methods:

1. **QGroundControl** (Beginner-friendly GUI)
2. **Python MAVSDK** (Programmatic control)
3. **ROS2** (Advanced robotics framework)

## Prerequisites

- **Operating System**: Ubuntu 22.04 Jammy Jellyfish (LTS) - **Required for stability**
- **Gazebo Version**: 
  - Gazebo Fortress (if using ROS2)
  - Gazebo Harmonic (if using MAVSDK or QGroundControl only)
- **PX4 Autopilot** and dependencies
- **QGroundControl**
- **Python 3.8+** with pip

## Gazebo Installation

### Option 1: Gazebo Fortress (Required for ROS2 Integration)

**Use this version if you plan to use ROS2 with your drone simulation.**

#### Step 1: Set up the Gazebo APT repository
```bash
sudo apt update
sudo apt install curl gnupg lsb-release
```

Add the OSRF key and repository:
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.osrfoundation.org/gazebo.key | sudo gpg --dearmor -o /etc/apt/keyrings/gazebo.gpg
```

Add the repository:
```bash
echo "deb [signed-by=/etc/apt/keyrings/gazebo.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
```

#### Step 2: Install Gazebo Fortress
```bash
sudo apt update
sudo apt install gz-fortress
```

Install development tools (optional):
```bash
sudo apt install gz-fortress-dev
```

#### Step 3: Verify Installation
```bash
gz sim --version
```

Expected output:
```
Gazebo Sim, version 6.X.X
Copyright (C) 2018 Open Source Robotics Foundation.
Released under the Apache 2.0 License.
```

#### Step 4: Test Installation
```bash
gz sim shapes.sdf
```

**Reference**: [Gazebo Fortress Installation Guide](https://gazebosim.org/docs/fortress/install_ubuntu/)

### Option 2: Gazebo Harmonic (For MAVSDK/QGroundControl Only)

**Use this version if you're only using MAVSDK or QGroundControl (no ROS2).**

#### Step 1: Set up the Gazebo APT repository
```bash
sudo apt update
sudo apt install curl gnupg lsb-release
```

Add the OSRF key and repository:
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.osrfoundation.org/gazebo.key | sudo gpg --dearmor -o /etc/apt/keyrings/gazebo.gpg
```

Add the repository:
```bash
echo "deb [signed-by=/etc/apt/keyrings/gazebo.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
```

#### Step 2: Install Gazebo Harmonic
```bash
sudo apt update
sudo apt install gz-harmonic
```

Install development tools (optional):
```bash
sudo apt install gz-harmonic-dev
```

#### Step 3: Verify Installation
```bash
gz sim --version
```

Expected output:
```
Gazebo Sim, version 8.X.X
Copyright (C) 2018 Open Source Robotics Foundation.
Released under the Apache 2.0 License.
```

#### Step 4: Test Installation
```bash
gz sim shapes.sdf
```
## Alternative: Build Gazebo Harmonic or Fortress from Source

If you are using **Ubuntu 24.04 Noble** or any unsupported distribution, you can build Gazebo Harmonic from source.
#### Go to [Gazebo Setup from Source](gazeboSetup.md)

**Reference**: [Gazebo Harmonic Installation Guide](https://gazebosim.org/docs/harmonic/install_ubuntu/)

## QGroundControl Installation

### Step 1: Download QGroundControl
Visit [QGroundControl Official Website](https://qgroundcontrol.com/) and download the latest AppImage for Linux.

### Step 2: Install QGroundControl
```bash
# Navigate to your Downloads folder
cd ~/Downloads

# Make the AppImage executable
chmod +x QGroundControl.AppImage

# Run QGroundControl
./QGroundControl.AppImage
```

**Optional**: Move to a permanent location:
```bash
sudo mv QGroundControl.AppImage /opt/
sudo ln -s /opt/QGroundControl.AppImage /usr/local/bin/qgroundcontrol
```

## PX4 Autopilot Setup

### Step 1: Clone PX4 Autopilot Repository
```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
```

### Step 2: Install PX4 Dependencies
```bash
bash ./Tools/setup/ubuntu.sh
```

**Note**: This script will install all necessary dependencies including build tools, Python packages, and simulation requirements.

### Step 3: Build PX4 for Gazebo Simulation

#### For Gazebo Fortress (ROS2 users):
```bash
PX4_SIM_MODEL=x500 PX4_GZ_VERSION=fortress make px4_sitl gz
```

#### For Gazebo Harmonic (MAVSDK/QGroundControl users):
```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500_depth
```

### Step 4: Test the Simulation
After building, you should see:
- Gazebo simulation window with the drone
- PX4 console output
- The drone should be ready to connect to QGroundControl

## Control Methods

### Method 1: QGroundControl (Beginner-Friendly)

#### Step 1: Start PX4 SITL
```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500_depth (For Deapth Cam)
make px4_sitl gz_x500 (No camera Installed, Physics Simulation Purpose)
```

#### Step 2: Connect QGroundControl
1. Launch QGroundControl
2. It should automatically detect and connect to the simulated drone
3. Use the GUI to arm, takeoff, and control the drone

### Method 2: Python MAVSDK Control

#### Step 1: Install MAVSDK for Python
```bash
pip install --upgrade pip
pip install mavsdk
```

#### Step 2: Download The Script From the repo


#### Step 3: Run the Control Script
Make sure PX4 SITL is running first
```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500_depth
```
In another terminal, run the Python script
```bash
python3 offboard_control.py
```



#### Step 2: Install PX4-ROS2 Bridge
Install required packages
```bash
sudo apt install ros-humble-px4-msgs
```
 Source ROS2 environment
 ```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Method 3: Control using ROS2 go to:  [Ros-Integration](Ros2-integration.md)

## Advanced Configuration

### Adding Virtual Camera

1. Navigate to the drone model directory:
```bash
cd ~/PX4-Autopilot/Tools/simulation/gz/models/x500
```

2. Edit the `model.sdf` file to add camera sensor configuration.

### Using Custom Worlds

1. Create your custom world file in SDF format
2. Place it in the appropriate Gazebo worlds directory
3. Run with custom world:
```bash
export PX4_GZ_WORLD=your_world_name
PX4_SIM_MODEL=x500 PX4_GZ_VERSION=harmonic make px4_sitl gz
```

### Available Models

### Multicopter
- `gz_x500` - Standard quadcopter  
- `gz_x500_vision` - Quadrotor with Visual Odometry  
- `gz_x500_depth` - Quadcopter with depth camera  
- `gz_x500_mono_cam` - Quadrotor with Monocular Camera  
- `gz_x500_mono_cam_down` - Quadrotor with Down-facing Monocular Camera  
- `gz_x500_lidar_down` - Quadrotor with Down-facing 1D LIDAR  
- `gz_x500_lidar_front` - Quadrotor with Front-facing 1D LIDAR  
- `gz_x500_lidar_2d` - Quadrotor with 2D LIDAR  
- `gz_x500_gimbal` - Quadrotor with Front-facing Gimbal  

### Plane / Fixed-Wing
- `gz_rc_cessna` - Standard fixed-wing plane  
- `gz_advanced_plane` - Advanced plane with configurable lift/drag physics  

### VTOL
- `gz_standard_vtol` - Standard VTOL  
- `gz_quadtailsitter` - VTOL Quad Tailsitter  
- `gz_tiltrotor` - VTOL Tiltrotor Plane  

### Rover
- `gz_r1_rover` - Differential Rover  
- `gz_rover_ackermann` - Ackermann Steering Rover  

## Troubleshooting

### Common Issues

1. **Gazebo not starting**: Check if you have the correct Gazebo version installed
2. **Connection refused**: Ensure PX4 SITL is running before connecting scripts
3. **Build errors**: Run `make distclean` and rebuild
4. **Permission errors**: Check file permissions and use `sudo` where necessary

### Useful Commands
Check Gazebo version
```bash
gz sim --version
```

 Clean PX4 build
 ```bash
cd ~/PX4-Autopilot && make distclean
```

 Check PX4 processes
```bash
ps aux | grep px4
```

Kill all PX4 processes
```bash
pkill -f px4
```

## References

- [PX4 Autopilot Documentation](https://docs.px4.io/)
- [Gazebo Fortress Documentation](https://gazebosim.org/docs/fortress)
- [Gazebo Harmonic Documentation](https://gazebosim.org/docs/harmonic)
- [MAVSDK Python Documentation](https://mavsdk.mavlink.io/main/en/)
- [QGroundControl User Guide](https://docs.qgroundcontrol.com/)
- [ROS2 Humble Documentation](https://docs.ros.org/en/humble/)

## Next Steps

1. Start with QGroundControl for basic understanding
2. Progress to Python MAVSDK for programmatic control
3. Explore ROS2 integration for advanced robotics applications
4. Experiment with different drone models and sensors
5. Create custom worlds and scenarios for testing

Happy flying! 🚁
