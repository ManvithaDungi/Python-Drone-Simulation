### Method 3: ROS2 Integration

#### Step 1: Install ROS2 Humble
Add ROS2 apt repository
```bash
sudo apt update
sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64,arm64] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'
```
Install ROS2 Humble
```bash
sudo apt update
sudo apt install ros-humble-desktop
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

#### Step 3: Build and Run ROS2 Bridge
Navigate to PX4 directory
```bash
cd ~/PX4-Autopilot
```
Build SITL with Gazebo (Fortress is recommended for ROS2):
```bash
PX4_SIM_MODEL=x500 PX4_GZ_VERSION=fortress make px4_sitl gz
```
(If you use Harmonic, ROS2 integration may fail due to some untested features.)

 In another terminal, run the microRTPS bridge
```bash
ros2 launch px4_ros_com offboard_control.launch.py
```

