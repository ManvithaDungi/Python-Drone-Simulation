# PX4 + Gazebo Harmonic Setup on WSL (Ubuntu)

This guide explains how to set up **PX4 SITL** with **Gazebo Harmonic (gz sim)** on **WSL (Windows Subsystem for Linux)**.

---

## 1. Prerequisites

### ✅ Install WSL & Ubuntu
- Ensure WSL2 is enabled.
- Install Ubuntu 22.04 or 24.04 via Microsoft Store.

### ✅ Update Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### ✅ Basic Development Tools
```bash
sudo apt install git wget curl lsb-release gnupg python3 python3-pip -y
```

---

## 2. Install Gazebo Harmonic

Gazebo Harmonic (gz sim v8.x) is the officially supported version for PX4.

### Step 1: Add Gazebo’s Repository
```bash
sudo apt remove gz-garden gz-fortress -y   # remove older versions if any

sudo apt update
sudo apt install lsb-release wget gnupg -y
sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list
```

### Step 2: Install Gazebo Harmonic
```bash
sudo apt update
sudo apt install gz-sim8 -y
```

### Step 3: Verify Installation
```bash
gz sim --version
# Output should be something like: Gazebo Sim, version 8.9.0
```

---

## 3. Clone PX4 Autopilot

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
```

⚠️ **If submodules fail to load:**  
```bash
git submodule update --init --recursive
```

---

## 4. Install PX4 Dependencies

### PX4 Common Setup
```bash
bash ./Tools/setup/ubuntu.sh
```

### Optional (for Python MAVSDK or ROS2 later)
```bash
pip install mavsdk
```

---

## 5. Run PX4 SITL with Gazebo Harmonic

### Default Test (x500 drone)
```bash
make px4_sitl gz_x500
```

### With Depth Camera
```bash
make px4_sitl gz_x500_depth
```

### Select a World
You can specify a world from `Tools/simulation/gz/worlds/`:
```bash
PX4_GZ_WORLD=default make px4_sitl gz_x500_depth
```

### Verify
- Gazebo GUI should launch with the selected world.
- PX4 SITL terminal will show:
```
INFO  [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
```

---

## 6. Useful Gazebo Commands

- **List Available Worlds**
```bash
ls PX4-Autopilot/Tools/simulation/gz/worlds
```

- **Manual GUI World Integration**  
Open Gazebo GUI and insert models/worlds directly from the **Insert Tab**.

- **Camera Views**  
Use the **GUI (Sensors → Camera / Depth Camera)** to switch between normal and depth views.

---

## 7. Troubleshooting

### ✅ Missing Submodules
```bash
git submodule update --init --recursive
```

### ✅ Build Errors (CMake / Ninja)
Clean build:
```bash
make clean
make distclean
```

### ✅ Version Conflicts
Ensure:
- PX4 is latest (`git pull origin main`)
- `gz sim --version` shows **v8.x** (Harmonic)

---

## 8. Next Steps

- Install **QGroundControl** for manual control (optional).
- Use **MAVSDK-Python** for autonomous control.

---

### References

- [PX4 Documentation](https://docs.px4.io/)
- [Gazebo Harmonic Docs](https://gazebosim.org/docs/harmonic)
