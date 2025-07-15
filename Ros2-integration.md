# Method 3: ROS2 Integration (Advanced Robotics Control)

This method allows controlling the PX4 drone in Gazebo using **ROS2 Humble** and the PX4-ROS2 bridge.

---

## ✅ Step 1: Install ROS2 Humble

Add the ROS2 apt repository:

```bash
sudo apt update
sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -
echo "deb [arch=amd64,arm64] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/ros2-latest.list
```

Install ROS2:

```bash
sudo apt update
sudo apt install ros-humble-desktop
```

Source ROS2 automatically every time you open a terminal:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ Step 2: Install PX4-ROS2 Bridge

Install PX4 ROS2 message packages:

```bash
sudo apt install ros-humble-px4-msgs
```

Clone the ROS2 PX4 Offboard workspace:

```bash
mkdir -p ~/ros2_px4_offboard_example_ws/src
cd ~/ros2_px4_offboard_example_ws/src
git clone https://github.com/ARK-Electronics/ROS2_PX4_Offboard_Example.git
```

Build the workspace:

```bash
cd ~/ros2_px4_offboard_example_ws
colcon build --symlink-install
```

Source your workspace after building:

```bash
source install/setup.bash
```

*(You need to run this command every time you open a new terminal for ROS2 work.)*

---

## ✅ Step 3: Build and Run PX4 SITL with ROS2

Run PX4 SITL in one terminal:

```bash
cd ~/PX4-Autopilot
PX4_SIM_MODEL=x500 PX4_GZ_VERSION=fortress make px4_sitl gz
```

In another terminal, run the ROS2 launch file:

```bash
cd ~/ros2_px4_offboard_example_ws
source install/setup.bash
ros2 launch px4_offboard offboard_velocity_control.launch.py
```

---

## 🔹 What Happens After Launch?

- **microRTPS bridge** starts automatically for ROS2 communication  
- **Gazebo** opens with the PX4 SITL simulation  
- **Offboard control node** starts, enabling ROS2-based drone control

---
