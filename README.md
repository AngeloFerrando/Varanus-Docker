# Varanus-Docker

A comprehensive robotic system for remote inspection and monitoring, combining ROS (Robot Operating System) with formal verification techniques and Docker containerization.

## Overview

Varanus-Docker is an integrated platform for autonomous robot control and remote inspection. The project combines:

- **Python** (58.1%) - Core system logic and monitoring
- **C++** (23%) - Performance-critical components
- **CMake** (10.6%) - Build system
- **Java** (4.9%) - Robotic framework integration
- **Docker** (1.7%) - Container orchestration
- **Shell Scripts** (1.7%) - Automation and utilities

## Features

- **Remote Inspection Capabilities** - Autonomous rover for remote monitoring and data collection
- **ROS Integration** - Full Robot Operating System support for distributed robotics control
- **Formal Verification** - CSP (Communicating Sequential Processes) models for system validation
- **Docker Containerization** - Portable deployment across different environments
- **Real-time Monitoring** - System monitoring and radiation detection capabilities
- **Distributed Architecture** - Java ROS bridge for cross-platform communication

## Project Structure

```
Varanus-Docker/
├── monitor.py                 # Core monitoring and system management
├── system_interface.py        # System interface for robot control
├── generate_csp.py            # CSP model generation for formal verification
├── RosEnv.java               # Java ROS environment configuration
├── Dockerfile                # Docker container configuration
├── run.sh                     # Main execution script
├── commands.sh               # Utility commands
├── rover_model3.csp          # CSP formal model of rover system
├── rover_model3.yaml         # YAML configuration for rover model
├── rover_defs3.csp           # CSP definitions and constants
├── radiation_varanus.yaml    # Radiation monitoring configuration
├── remote_inspection.ail      # Inspection logic and rules
├── java_rosbridge_all.jar    # ROS bridge for Java integration
├── varanus_model3.png        # System architecture diagram
├── radiation_ws/             # Radiation workspace directory
└── csp/                       # Generated CSP models directory
```

## Key Components

### Monitoring System (`monitor.py`)
Handles real-time monitoring, system status tracking, and radiation detection for the remote inspection rover.

### System Interface (`system_interface.py`)
Provides the main interface for controlling and communicating with the robotic system through ROS.

### Formal Verification (CSP Models)
- `rover_model3.csp` - Formal specification of rover behavior
- `rover_defs3.csp` - System definitions and constants
- `generate_csp.py` - Automated generation of CSP models from specifications

### Configuration
- `rover_model3.yaml` - YAML-based rover configuration
- `radiation_varanus.yaml` - Radiation monitoring parameters
- `remote_inspection.ail` - Inspection logic and autonomous rules

## Requirements

- Docker (for containerized deployment)
- ROS (Robot Operating System)
- Python 3.x
- Java 8 or higher (for ROS bridge)
- C++ compiler with CMake build system

## Installation

### Using Docker

```bash
docker build -t varanus-docker .
docker run -it varanus-docker
```

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/AngeloFerrando/Varanus-Docker.git
cd Varanus-Docker
```

2. Install dependencies and build:
```bash
./run.sh
```

3. Configure the system:
```bash
./commands.sh
```

## Usage

### Starting the System

```bash
./run.sh
```

### Monitoring Operations

Run the monitor to track system status:
```bash
python3 monitor.py
```

### System Control

Interact with the robotic system:
```bash
python3 system_interface.py
```

### Formal Verification

Generate and verify CSP models:
```bash
python3 generate_csp.py
```

## Configuration

Customize system behavior through YAML configuration files:

- `rover_model3.yaml` - Rover parameters and settings
- `radiation_varanus.yaml` - Radiation monitoring thresholds and behavior

## Architecture

The system employs a distributed architecture:

```
┌─────────────────────────────────────────┐
│         Remote Inspection Rover         │
│           (Varanus Model 3)             │
├─────────────────────────────────────────┤
│  ROS (Robot Operating System)           │
│  - Java ROS Bridge                      │
│  - Python Control Interfaces            │
│  - C++ Performance Components           │
├─────────────────────────────────────────┤
│  Formal Verification (CSP)              │
│  - Model-based system validation        │
│  - Safety property verification         │
│  - Autonomous inspection logic          │
├─────────────────────────────────────────┤
│  Docker Container Environment           │
│  - Isolated, portable deployment        │
│  - Cross-platform compatibility         │
└─────────────────────────────────────────┘
```

## Development

This project combines:
- **Systems Programming**: C++ for critical components
- **Scripting & Automation**: Python for control and monitoring
- **Formal Methods**: CSP models for system verification
- **Robotics**: ROS framework for robot control and communication
- **Containerization**: Docker for reproducible environments

## License

See LICENSE file for details.

## Author

[Angelo Ferrando](https://github.com/AngeloFerrando)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

For more information about the project or specific components, please refer to the individual files and their documentation.
