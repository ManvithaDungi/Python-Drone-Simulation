## Alternative: Build Gazebo Harmonic from Source

If you are using **Ubuntu 24.04 Noble** or any unsupported distribution, you can build Gazebo Harmonic from source.

### Step 1: Install Build Dependencies
```bash
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  git \
  wget \
  lsb-release \
  gnupg \
  python3 \
  python3-colcon-common-extensions \
  python3-vcstool \
  qtbase5-dev \
  libtinyxml2-dev
```

### Step 2: Download Gazebo Harmonic Source

```bash
mkdir -p ~/gz_ws/src
cd ~/gz_ws
wget https://raw.githubusercontent.com/gazebo-tooling/gazebodistro/master/collection-harmonic.yaml
vcs import src < collection-harmonic.yaml
```
### Step 3: Build Gazebo Harmonic

```bash
cd ~/gz_ws
colcon build --merge-install
```
### Step 4: Source the Environment
Add to your .bashrc for persistence
```bash
echo "source ~/gz_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Step 5: Verify Installation
```bash
gz sim --version
```

Expected Output: 
```
Gazebo Sim, version 8.X.X
```

Now you can use this source-built version with PX4 and MAVSDK.

# Gazebo Fortress - Source Installation Guide

If you are using **Ubuntu 24.04 Noble** or an unsupported distribution, you can build Gazebo Fortress from source.

## Step 1: Install Build Dependencies
```bash
sudo apt update
sudo apt install -y   build-essential   cmake   git   wget   lsb-release   gnupg   python3   python3-colcon-common-extensions   python3-vcstool   qtbase5-dev   libtinyxml2-dev
```

## Step 2: Download Gazebo Fortress Source
```bash
mkdir -p ~/gz_ws/src
cd ~/gz_ws
wget https://raw.githubusercontent.com/gazebo-tooling/gazebodistro/master/collection-fortress.yaml
vcs import src < collection-fortress.yaml
```

## Step 3: Build Gazebo Fortress
```bash
cd ~/gz_ws
colcon build --merge-install
```

## Step 4: Source the Environment
Add to your `.bashrc` for persistence:
```bash
echo "source ~/gz_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Step 5: Verify Installation
```bash
gz sim --version
```

Expected Output:
```
Gazebo Sim, version 6.X.X
```

Now you can use this source-built version with PX4 and ROS2.

**Reference:** [Gazebo Fortress Source Build Guide](https://gazebosim.org/docs/fortress/install_ubuntu_src)
