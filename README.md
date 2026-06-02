# Varanus-Docker

A comprehensive Docker-based framework for autonomous robot inspection and monitoring, integrating formal verification (CSP-based runtime verification), real-time monitoring, and robotic control using ROS.

## Overview

Varanus-Docker is an integrated platform that demonstrates formal verification techniques applied to autonomous robotic systems. It combines multiple verification and monitoring frameworks into a single, reproducible Docker environment for a remote inspection rover use case.

The system integrates three key frameworks:

- **[ROSMonitoring](https://github.com/autonomy-and-verification-uol/ROSMonitoring)** - Runtime verification framework for ROS systems
- **[Varanus](https://github.com/autonomy-and-verification/varanus)** - Runtime verification toolchain using CSP (Communicating Sequential Processes) models as oracles
- **[PredictiveVaranus](https://github.com/AngeloFerrando/PredictiveVaranus)** - Predictive extension of Varanus for forecasting system behavior

### Language Composition

- **Python** (58.1%) - Core monitoring, verification, and system logic
- **C++** (23%) - Performance-critical ROS components and simulation plugins
- **CMake** (10.6%) - Build system for ROS packages
- **Java** (4.9%) - Autonomous agent framework (MCAPL)
- **Docker** (1.7%) - Container orchestration
- **Shell** (1.7%) - Automation and utilities

## Key Features

- **Formal Verification** - CSP-based oracle models for system validation using Varanus
- **Predictive Monitoring** - Forecast system behavior using PredictiveVaranus
- **Runtime Monitoring** - Real-time property verification with ROSMonitoring
- **Autonomous Agents** - Autonomous inspection logic using MCAPL (Agent programming language)
- **Robot Simulation** - Gazebo simulator with custom radiation detection plugins
- **Full ROS Integration** - Complete Robot Operating System with all necessary tools
- **Radiation Monitoring** - Real-time radiation detection and tracking capabilities
- **Reproducible Environment** - Everything packaged in Docker for consistent execution

## Project Structure

```
Varanus-Docker/
├── Dockerfile                      # Complete Docker image definition
├── commands.sh                     # Reference guide for manual commands (not a setup script)
├── run.sh                          # Main execution script
│
├── Formal Verification Models
├── rover_model3.csp               # CSP specification of rover behavior
├── rover_defs3.csp                # CSP definitions and constants
├── generate_csp.py                # Automated CSP generation from specifications
│
├── Configuration Files
├── rover_model3.yaml              # Rover parameters and settings
├── radiation_varanus.yaml         # Radiation monitoring configuration
├── remote_inspection.ail          # MCAPL agent logic for autonomous inspection
│
├── ROS and Agent Components
├── RosEnv.java                    # Java ROS environment configuration
├── java_rosbridge_all.jar         # ROS bridge for Java agent integration
├── system_interface.py            # System interface for robot control
├── radiation_ws/                  # ROS workspace with custom plugins
│
└── Architecture & Documentation
    └── varanus_model3.png         # System architecture diagram
```

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│          Autonomous Rover Inspection System                  │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐         ┌──────────┐
    │ Gazebo  │         │   ROS   │         │  MCAPL   │
    │Simulator│         │ System  │         │ Agent    │
    │ +Plugins│         │         │         │          │
    └────┬────┘         └────┬────┘         └────┬─────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Varanus  │        │ROS Monitor│       │Predictive│
    │ Runtime  │        │ (Reelay)  │       │ Varanus  │
    │Verification       │           │       │          │
    └──────────┘        └──────────┘       └──────────┘
        ▲                    ▲                    ▲
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    Property Verification
```

## Quick Start

### Prerequisites

- **Docker** (with NVIDIA GPU support optional for visualization)
- At least 10GB of disk space
- 4GB RAM minimum (8GB recommended)

### Build and Run

1. **Build the Docker image:**
   ```bash
   docker build -t varanus-docker .
   ```

2. **Run the container:**
   ```bash
   docker run -it varanus-docker
   ```

3. **Inside the container, you can run individual components** (see Usage section below)

## Usage

Once inside the Docker container, you can execute various components:

### Simulation Setup
```bash
# Launch Gazebo simulator with radiation plugins
roslaunch gazebo_radiation_plugins radiation_demonstrator_agent.launch

# Launch without GUI (for headless execution)
roslaunch gazebo_radiation_plugins radiation_demonstrator_agent.launch gui:=false
```

### Runtime Monitoring
```bash
# Run the ROS monitoring system
roslaunch monitor run_monitor.launch

# Run the formal verification oracle
python3 oracle.py --discrete --property examples.radiation.radiation_orange --port 8080 --online
```

### Autonomous Agent Execution
```bash
# Execute the autonomous inspection agent
java -cp ".:lib/3rdparty/*:bin" ail.mas.AIL ./src/examples/gwendolen/compositional/rain/remote_inspection/remote_inspection.ail
```

### System Monitoring with Verification
```bash
# Monitor mission completion with formal verification
python3 monitor.py \
  ../varanus/inspection-rover-test/rover_model3.yaml \
  "F mission_complete" \
  --online \
  --varanus-script ../varanus/varanus-python/varanus.py \
  --varanus-python /usr/bin/python2.7
```

### Cleanup
```bash
# Kill simulator processes if needed
pkill -9 gzserver && pkill -9 gzclient
```

## Configuration

Customize system behavior through configuration files:

### Rover Configuration (`rover_model3.yaml`)
Defines rover parameters, movement capabilities, and mission objectives.

### Radiation Monitoring (`radiation_varanus.yaml`)
Sets radiation detection thresholds and monitoring behavior.

### Autonomous Logic (`remote_inspection.ail`)
Defines the inspection mission logic and decision-making rules for the autonomous agent.

### Formal Specifications (CSP Models)
- `rover_model3.csp` - Formal specification of expected rover behavior
- `rover_defs3.csp` - System constants and type definitions

## Dependencies

The Docker image automatically installs:

- **ROS Noetic** - Full Robot Operating System with Jackal simulator
- **Python 3.8+** - Monitoring and control scripts
- **Python 2.7** - Legacy compatibility for some Varanus components
- **Java 17** - MCAPL agent framework
- **Gazebo** - Robot simulation with custom radiation plugins
- **FDR** - CSP model checker for formal verification
- **SPOT** - Automata manipulation library
- **Reelay** - Temporal logic monitoring library

## Development

### Adding New Properties

1. Define formal specifications in CSP models (`rover_model*.csp`)
2. Generate monitoring rules using `generate_csp.py`
3. Add agent logic to `remote_inspection.ail`
4. Test with the monitoring framework

### Extending the Framework

- Modify `rover_model3.yaml` for new rover capabilities
- Update `radiation_varanus.yaml` for different detection parameters
- Extend the MCAPL agent for additional autonomous behaviors
- Add new Gazebo plugins for additional simulation features

## Related Projects

- **[ROSMonitoring](https://github.com/autonomy-and-verification-uol/ROSMonitoring)** - Runtime verification for ROS
- **[Varanus](https://github.com/autonomy-and-verification/varanus)** - CSP-based runtime verification
- **[PredictiveVaranus](https://github.com/AngeloFerrando/PredictiveVaranus)** - Predictive verification extension
- **[MCAPL](https://github.com/mcapl/mcapl)** - Agent programming language framework

## License

See LICENSE file for details.

## Author

[Angelo Ferrando](https://github.com/AngeloFerrando)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Note:** The `commands.sh` file is a reference guide of useful commands to execute inside the Docker container. It is not meant to be run as a setup script.
