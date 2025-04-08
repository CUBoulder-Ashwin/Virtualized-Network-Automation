import subprocess

def run_cmd(cmd, capture_output=False, silent=False):
    if not silent:
        print(f"\n>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0 and not silent:
        print(f"Error: Command failed with exit code {result.returncode}")
        if capture_output:
            print(result.stderr)
    if capture_output:
        return result.stdout.strip()
    return result.returncode

def get_valid_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid integer.")

def get_existing_networks_with_subnets():
    output = run_cmd("docker network ls --format '{{.Name}}'", capture_output=True)
    network_names = output.splitlines()
    networks = []
    for net in network_names:
        subnet = run_cmd(
            f"docker network inspect {net} --format '{{{{(index .IPAM.Config 0).Subnet}}}}'",
            capture_output=True,
            silent=True
        )
        if not subnet or "error" in subnet.lower():
            subnet = "N/A"
        networks.append((net, subnet))
    return networks

def create_bgp_config():
    print(f"Creating BGP config file")
    local_as = get_valid_int("Enter local AS number: ")
    router_id = input("Enter router ID (e.g., '10.10.10.3'): ")

    # Neighbors
    neighbors = []
    num_neighbors = get_valid_int("\nHow many neighbors do you want to configure? ")
    for i in range(num_neighbors):
        print(f"\n--- Neighbor #{i+1} ---")
        address = input("Enter neighbor IP address: ")
        remote_as = get_valid_int("Enter neighbor remote AS number: ")
        neighbors.append({"address": address, "remote_as": remote_as})

    # Routes to advertise
    routes = []
    num_routes = get_valid_int("\nHow many routes do you want to advertise? ")
    for i in range(num_routes):
        prefix = input(f"Enter route prefix #{i+1} (e.g., '30.30.30.0/24'): ")
        routes.append({"prefix": prefix})

    # SSH
    ssh_username = input("\nEnter SSH username (e.g., 'ryu'): ")
    ssh_password = input("Enter SSH password (e.g., 'ryu'): ")

    # Write config to file
    with open("bgp_config.conf", "w") as config_file:
        config_file.write("BGP = {\n")
        config_file.write(f"    'local_as': {local_as},\n")
        config_file.write(f"    'router_id': '{router_id}',\n")
        config_file.write("    'neighbors': [\n")
        for neighbor in neighbors:
            config_file.write(f"        {{'address': '{neighbor['address']}', 'remote_as': {neighbor['remote_as']}}},\n")
        config_file.write("    ],\n")
        config_file.write("    'routes': [\n")
        for route in routes:
            config_file.write(f"        {{'prefix': '{route['prefix']}' }},\n")
        config_file.write("    ],\n")
        config_file.write("}\n\n")
        config_file.write("SSH = {\n")
        config_file.write(f"    'ssh_port': 4990,\n")
        config_file.write(f"    'ssh_host': '0.0.0.0',\n")
        config_file.write(f"    'ssh_username': '{ssh_username}',\n")
        config_file.write(f"    'ssh_password': '{ssh_password}',\n")
        config_file.write("}\n")

    print("\nBGP configuration file 'bgp_config.conf' created successfully.")
    print("-------------------------------------------------------------------------------------------------------------------------")

def create_docker_container():
    print(f"\nCreating ryu-bgp container")
    name = input("Enter container name: ")
    image = input("Enter Docker image (e.g., 'ryu-sdn-controller'): ")

    net_count = get_valid_int("\nHow many Docker networks do you want to attach? ")
    networks_info = []
    for i in range(net_count):
        print(f"\n--- Network #{i+1} ---")
        choice = input(f"Create new network for Network #{i+1}? (y/n): ").strip().lower()
        if choice == 'y':
            net_name = input("Enter new Docker network name: ")
            subnet = input("Enter subnet (e.g., '10.10.10.0/24'): ")
            run_cmd(f"docker network create --subnet={subnet} {net_name}")
        else:
            networks = get_existing_networks_with_subnets()
            print("\nAvailable Docker networks:")
            for idx, (net, subnet) in enumerate(networks, 1):
                print(f"{idx}. {net} (Subnet: {subnet})")
            while True:
                try:
                    selected = int(input("Select a network by number: "))
                    if 1 <= selected <= len(networks):
                        net_name, subnet = networks[selected - 1]
                        break
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
        ip = input(f"Assign IP to container in this network (based on {subnet}): ")
        networks_info.append((net_name, subnet, ip))

    print("\nStarting container...")
    run_cmd(f"docker run -dit --privileged --name {name} --network {networks_info[0][0]} --ip {networks_info[0][2]} {image} /bin/bash")

    for net_name, _, ip in networks_info[1:]:
        run_cmd(f"docker network connect --ip {ip} {net_name} {name}")

    print(f"\nDocker container '{name}' created and started successfully.")
    print("-------------------------------------------------------------------------------------------------------------------------")
    return name

def copy_config_to_container(container_name):
    print("Copying config file into the ryu-bgp container")
    run_cmd(f"docker cp bgp_config.conf {container_name}:/root/bgp_config.conf")
    print("\nBGP configuration file copied to the container successfully.")
    print("-------------------------------------------------------------------------------------------------------------------------")

def run_ryu_bgp_application(container_name):
    print("Running ryu-bgp app")
    command = (
        f"docker exec {container_name} "
        f"ryu-manager /usr/local/lib/python3.9/site-packages/ryu/services/protocols/bgp/application.py "
        f"--bgp-app-config-file /root/bgp_config.conf &"
    )
    run_cmd(command, silent=True)
    print("\nRyu BGP application started successfully in the background.")
    print("-------------------------------------------------------------------------------------------------------------------------")

def main():
    create_bgp_config()
    container_name = create_docker_container()
    copy_config_to_container(container_name)
    run_ryu_bgp_application(container_name)

if __name__ == "__main__":
    main()
