# FRR Routing
## Build the Image
To build the Docker image, run the following command in the directory containing your Dockerfile:
```
docker build -f Dockerfile.frr -t frr-ubuntu .
```


## Run the Python Script
The script (`frr_container.py`) guides you through setting up the FRR container, networks, and BGP configuration.
```
python3 frr_container.py
```


## What the Script Does (Step-by-Step)
1. 🚀 Container Initialization
   - Prompts the user to enter:
     - A container name.
     - The Docker image name (e.g., frr-ubuntu).

2. 🌐 Docker Network Setup
   - Asks how many Docker networks you want to connect.
   - For each network:
     - Option to create a new network with a specified subnet.
     - Or select an existing Docker network from a displayed list.
     - You assign an IP to the container in that network.

3. 📦 Container Deployment
   - Creates the Docker container with the first network and IP.
   - Connects it to all additional networks with specified IPs.

4. 🔐 Enable BGP Daemon
   - Updates `/etc/frr/daemons` inside the container to enable BGP:
     ```
     echo 'bgpd=yes' > /etc/frr/daemons
     ```

5. 🛠️ BGP Configuration (Dynamic)
   - Prompts you to input:
     - Your BGP AS number.
     - Number of neighbors.
     - Each neighbor’s IP and AS number.
     - List of networks to advertise (comma-separated).

6. 📝 Auto-Generates frr.conf
   - Builds and writes the entire FRR config dynamically:
     - Enables prefix lists and route-maps.
     - Configures all BGP peers and advertised networks.
     - Saves the config in `/etc/frr/frr.conf`.

7. 🔄 Restart & Verify FRR
   - Restarts the FRR service inside the container.
   - Shows the running BGP configuration using:
     ```
     vtysh -c "show running-config"
     ```


## Sample Interaction Flow
```
Enter container name: frr1 
Enter Docker image: frr-ubuntu

How many Docker networks do you want to attach? 2

— Network #1 — 
Do you want to create a new network for Network #1? (y/n): y 
Enter new Docker network name: net1 Enter subnet (e.g., 10.10.10.0/24): 10.10.10.0/24 
Assign IP to container in this network (based on 10.10.10.0/24): 10.10.10.2

— Network #2 — 
Do you want to create a new network for Network #2? (y/n): n 
Available Docker networks:
1.bridge (Subnet: N/A)
2.net2 (Subnet: 10.20.20.0/24)

Select a network by number: 2 
Assign IP to container in this network (based on 10.20.20.0/24): 10.20.20.2

Enter your BGP AS number: 65001 
How many BGP neighbors do you want to configure? 1

— Neighbor #1 — 
Neighbor IP: 10.20.20.3 
Neighbor AS number: 65002
Enter networks to advertise: 10.10.10.0/24,10.20.20.0/24: 20.20.20.0/24
```
---

## 💡 Requirements
- **Docker** (and Docker Engine running)
- **Python 3.x**
- Basic networking understanding (for BGP, IP ranges, subnets)

---

## 🚨 Troubleshooting
- **Docker Build Errors**: Ensure all dependencies are correctly installed and the Dockerfile is properly formatted.
- **Python Script Errors**: Check for syntax errors or issues with user input handling.
- **FRR Configuration Issues**:

  Verify if the `/etc/frr/frr.config` is correct and properly applied.

  Verify if the `bgpd=yes` in `/etc/frr/daemons`.

  Verify the route map in the bgp configuration.

If you encounter any issues, review the Docker logs and the output of the Python script for clues. Adjustments might be needed based on your specific environment or requirements.
