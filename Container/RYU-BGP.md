# 🧠 Ryu BGP App

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

