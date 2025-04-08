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

def setup_frr_container():
    name = input("Enter container name: ")
    image = input("Enter Docker image (e.g., frr-ubuntu): ")

    net_count = get_valid_int("\nHow many Docker networks do you want to attach? ")
    networks_info = []

    for i in range(net_count):
        print(f"\n--- Network #{i+1} ---")
        choice = input(f"Do you want to create a new network for Network #{i+1}? (y/n): ").strip().lower()
        if choice == 'y':
            net_name = input("Enter new Docker network name: ")
            subnet = input("Enter subnet (e.g., 10.10.10.0/24): ")
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

    print("-------------------------------------------------------------------------------------------------------------------------")
    
    print("\nStarting container...")
    run_cmd(f"docker run -dit --privileged --name {name} --network {networks_info[0][0]} --ip {networks_info[0][2]} {image} /bin/bash")

    for net_name, _, ip in networks_info[1:]:
        run_cmd(f"docker network connect --ip {ip} {net_name} {name}")
    print("-------------------------------------------------------------------------------------------------------------------------")
    
    print("\nStarting BGP...")
    run_cmd(f"docker exec {name} bash -c \"echo 'bgpd=yes' > /etc/frr/daemons\"")

    bgp_as = input("\nEnter your BGP AS number: ")
    neighbor_count = get_valid_int("How many BGP neighbors do you want to configure? ")

    neighbors = []
    for i in range(neighbor_count):
        print(f"\n--- Neighbor #{i+1} ---")
        neighbor_ip = input("Neighbor IP: ")
        neighbor_as = input("Neighbor AS number: ")
        neighbors.append((neighbor_ip, neighbor_as))

    advertised_nets = input("\nEnter networks to advertise (comma-separated, e.g., 10.10.10.0/24,10.20.20.0/24): ").split(',')

    frr_conf = [
        "frr version 10.4-dev-DockerBuild",
        "frr defaults traditional",
        "log syslog informational",
        "no ipv6 forwarding",
        "service integrated-vtysh-config",
        "!",
        "ip prefix-list ALL-IPv4 seq 5 permit 0.0.0.0/0 le 32",
        "route-map ACCEPT_ALL permit 10",
        " match ip address prefix-list ALL-IPv4",
        "!"
    ]
    frr_conf += [f"router bgp {bgp_as}"]
    for neighbor_ip, neighbor_as in neighbors:
        frr_conf.append(f" neighbor {neighbor_ip} remote-as {neighbor_as}")
    frr_conf.append("!")
    frr_conf.append(" address-family ipv4 unicast")
    for net in advertised_nets:
        frr_conf.append(f"  network {net.strip()}")
    for neighbor_ip, _ in neighbors:
        frr_conf.append(f"  neighbor {neighbor_ip} route-map ACCEPT_ALL in")
        frr_conf.append(f"  neighbor {neighbor_ip} route-map ACCEPT_ALL out")
    frr_conf += [" exit-address-family", "exit", "!", "end"]

    config_str = '\n'.join(frr_conf)
    print("\nWriting frr.conf...")
    run_cmd(f"docker exec {name} bash -c \"echo '{config_str}' > /etc/frr/frr.conf\"")
    print("-------------------------------------------------------------------------------------------------------------------------")

    print("\nRestarting FRR...")
    run_cmd(f"docker exec {name} env PYTHONWARNINGS='ignore::SyntaxWarning' systemctl restart frr")
    run_cmd(f"docker exec {name} env PYTHONWARNINGS='ignore::SyntaxWarning' systemctl status frr")
    print("-------------------------------------------------------------------------------------------------------------------------")

    print("\n==== FRR Running Config ====")
    output = run_cmd(f"docker exec {name} vtysh -c 'show running-config'", capture_output=True)
    print(output)
    print("-------------------------------------------------------------------------------------------------------------------------")

if __name__ == "__main__":
    setup_frr_container()
