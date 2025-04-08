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



