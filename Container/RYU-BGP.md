# Ryu BGP App

This python file automates the deployment of **Ryu BGP** inside Docker containers using a Python script. It simplifies container creation, Docker network configuration, and BGP setup via user inputs—making it easy to spin up full routing topologies without manually editing config files.

---

## Build the Docker Image

Before running the automation, you need to build the Docker image with Ryu BGP installed. Make sure you have a file named `Dockerfile.ryu` in your project directory with the appropriate Ryu BGP installation commands. To build the Docker image, run the following command in the directory containing your Dockerfile:
```
docker build -f Dockerfile.ryu -t ryu-sdn-controller .
```

## Run the Python Script
The script (`ryu_bgp_container.py`) guides you through setting up the Ryu BGP container, networks, and BGP configuration.
```
python3 ryu_bgp_container.py
```

## What the Script Does (Step-by-Step)
1. 📝 Create BGP Configuration
   - Prompts the user to enter:
     - Local AS number.
     - Router ID.
     - Number of neighbors and their details.
     - Routes to advertise.
     - SSH credentials.
   - Generates a BGP configuration file (`bgp_config.conf`).

2. 🌐 Docker Network Setup
   - Asks how many Docker networks you want to connect.
   - For each network:
     - Option to create a new network with a specified subnet.
     - Or select an existing Docker network from a displayed list.
     - You assign an IP to the container in that network.

3. 📦 Container Deployment
   - Creates the Docker container with the first network and IP.
   - Connects it to all additional networks with specified IPs.

4. 📁 Copy Config to Container
   - Copies the generated BGP configuration file into the container.

5. 🔄 Run Ryu BGP Application
   - Starts the Ryu BGP application inside the container using the provided configuration.

## Sample Interaction Flow
```
Enter local AS number: 65001
Enter router ID (e.g., ‘10.10.10.3’): 10.10.10.3
How many neighbors do you want to configure? 1

— Neighbor #1 —
Enter neighbor IP address: 10.20.20.3
Enter neighbor remote AS number: 65002
How many routes do you want to advertise? 2
Enter route prefix #1 (e.g., ‘30.30.30.0/24’): 10.10.10.0/24
Enter route prefix #2 (e.g., ‘30.30.30.0/24’): 10.20.20.0/24

Enter SSH username (e.g., ‘ryu’): ryu
Enter SSH password (e.g., ‘ryu’): ryu

Enter container name: ryu1
Enter Docker image (e.g., ‘ryu-sdn-controller’): ryu-sdn-controller
How many Docker networks do you want to attach? 2

— Network #1 —
Create new network for Network #1? (y/n): y
Enter new Docker network name: net1
Enter subnet (e.g., ‘10.10.10.0/24’): 10.10.10.0/24
Assign IP to container in this network (based on 10.10.10.0/24): 10.10.10.2

— Network #2 —
Create new network for Network #2? (y/n): n
Available Docker networks:
1. bridge (Subnet: N/A)
2. net2 (Subnet: 10.20.20.0/24)
Select a network by number: 2
Assign IP to container in this network (based on 10.20.20.0/24): 10.20.20.2
```

---

## 💡 Requirements
- **Docker** (and Docker Engine running)
- **Python 3.9**
- **Paramiko** - to SSH into the bgp engine and check the configurations
- Basic networking understanding (for BGP, IP ranges, subnets)

---
## 🚨 Troubleshooting
- **Docker Build Errors**: Ensure all dependencies are correctly installed and the Dockerfile is properly formatted.
- **Python Script Errors**: Check for syntax errors or issues with user input handling.
- **RYU Configuration Issues**:
  Verify that the `bgp_config.conf` configuration is correct and properly applied.
  Check the python version. It should be 3.9 and older.
  Check the eventlet version.

If you encounter any issues, review the Docker logs and the output of the Python script for clues. Adjustments might be needed based on your specific environment or requirements.
