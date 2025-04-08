import sys
import time

def virtual_servers(conn):
    while True:
        print("\nVirtual Server menu")
        print("1. Create")
        print("2. Delete")
        print("3. List")
        print("4. Main menu")
        choice = input("Select an option (1-4) or type 'exit': ")

        if choice == "1":
            create(conn)
        elif choice == "2":
            delete(conn)
        elif choice == "3":
            list_servers(conn)
        elif choice == "4":
            print("Returning to main menu...")
            break
        elif choice == "exit":
            print("Exiting application....")
            sys.exit(0)
            

def create(conn):
    try:
        num_servers = int(input("\nEnter the number of virtual servers to create: "))

        created_servers = []
        for i in range(num_servers):
            s_name = input(f"Enter name for server {i+1}: ")

            # List available images
            print("\nAvailable Images:")
            images = list(conn.image.images())
            for j, image in enumerate(images, start=1):
                print(f"{j}. {image.name} ({image.id})")
            choice_image = input(f"Select the image for server {i+1} (1-{len(images)}): ")
            try:
                choice_image = int(choice_image)
                if 1 <= choice_image <= len(images):
                    s_image = images[choice_image - 1].id
                else:
                    print("Invalid choice. Using default image.")
                    s_image = images[0].id
            except ValueError:
                print("Invalid input. Using default image.")
                s_image = images[0].id

            # List available flavors
            print("\nAvailable Flavors:")
            flavors = list(conn.compute.flavors())
            for j, flavor in enumerate(flavors, start=1):
                print(f"{j}. {flavor.name} ({flavor.id})")
            choice_flavor = input(f"Select the flavor for server {i+1} (1-{len(flavors)}): ")
            try:
                choice_flavor = int(choice_flavor)
                if 1 <= choice_flavor <= len(flavors):
                    s_flavor = flavors[choice_flavor - 1].id
                else:
                    print("Invalid choice. Using default flavor.")
                    s_flavor = flavors[0].id
            except ValueError:
                print("Invalid input. Using default flavor.")
                s_flavor = flavors[0].id

            # List available networks
            print("\nAvailable Networks:")
            networks = list(conn.network.networks())
            for j, network in enumerate(networks, start=1):
                print(f"{j}. {network.name} ({network.id})")
            choice_network = input(f"Select the network for server {i+1} (1-{len(networks)}): ")
            try:
                choice_network = int(choice_network)
                if 1 <= choice_network <= len(networks):
                    s_network = networks[choice_network - 1].id
                else:
                    print("Invalid choice. Using default network.")
                    s_network = networks[0].id
            except ValueError:
                print("Invalid input. Using default network.")
                s_network = networks[0].id

            # Create server
            server = conn.compute.create_server(
                name=s_name,
                flavor_id=s_flavor,
                image_id=s_image,
                networks=[{"uuid": s_network}]
            )

            created_servers.append(server)
            print("\n**********************************************************")
            print(f"Created server {server.name}")
            print("**********************************************************")
            print("\n")
            # Wait for the server status to become ACTIVE
            while True:
                server = conn.compute.get_server(server.id)
                if server.status == 'ACTIVE':
                    print(f"Server {server.name} is now ACTIVE.")
                    break  # Exit the loop when the server is ACTIVE
                else:
                    print(f"Server {server.name} is in {server.status} state. Waiting...")
                    time.sleep(10)  # Wait for 5 seconds before checking again

            # Confirm server is ACTIVE
            if server.status != 'ACTIVE':
                print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                print(f"Error: Server {server.name} did not reach ACTIVE state.")
                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                continue

            # Ask user if they want to assign a floating IP
            assign_floating_ip = input("\nAssign a floating IP? (yes/no): ").strip().lower()
            if assign_floating_ip == "yes":
                # Get the public network ID dynamically
                public_network = None
                for network in conn.network.networks():
                    if network.name.lower() == "public":  # Ensure case-insensitive match
                        public_network = network.id
                        break

                if public_network:
                    # Create and allocate a floating IP
                    floating_ip = conn.network.create_ip(floating_network_id=public_network)

                    if floating_ip:
                        try:
                            # Associate the floating IP with the server
                            # First, get the port ID of the server
                            ports = list(conn.network.ports(device_id=server.id))
                            if ports:
                                port_id = ports[0].id
                                conn.network.update_ip(floating_ip.id, port_id=port_id)
                                print("\n**********************************************************")
                                print(f"Assigned Floating IP: {floating_ip.floating_ip_address} to server {server.name}")
                                print("**********************************************************")
                            else:
                                print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                                print("Error: Could not find a port for the server.")
                                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                        except Exception as e:
                            print(f"Error assigning floating IP: {e}")
                    else:
                        print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                        print("Error: Failed to allocate a floating IP.")
                        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                else:
                    print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                    print("Error: No public network found. Please check your OpenStack network setup.")
                    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

            # Ask user if they want to create a security group
            create_sec_group = input("\nAllow all traffic to the internet? (yes/no): ").strip().lower()
            if create_sec_group == "yes":
                sec_group_name = f"{server.name}-security-group"
                sec_group_description = f"Security group for {server.name}"

                # Create security group
                sec_group = conn.network.create_security_group(name=sec_group_name, description=sec_group_description)

                # Add rules to allow all traffic (adjust as needed)
                conn.network.create_security_group_rule(
                    security_group_id=sec_group.id,
                    direction='ingress',
                    protocol='tcp',
                    port_range_min=1,
                    port_range_max=65535,
                    remote_ip_prefix='0.0.0.0/0'  # Allow all IPs
                )
                conn.network.create_security_group_rule(
                    security_group_id=sec_group.id,
                    direction='egress',
                    protocol='tcp',
                    port_range_min=1,
                    port_range_max=65535,
                    remote_ip_prefix='0.0.0.0/0'  # Allow all IPs
                )
                
                # Attach the security group to the server
                conn.compute.add_security_group_to_server(server=server, security_group=sec_group)

                print("\n**********************************************************")
                print(f"Created and assigned security group: {sec_group_name} to server {server.name}")
                print("**********************************************************")

        return created_servers

    except Exception as e:
        print(f"Error creating servers: {e}")


def delete(conn):
    print("\nSelect the server you want to delete:")
    servers = list(conn.compute.servers())  # Convert generator to list
    for i, server in enumerate(servers, start=1):
        print(f"{i}. {server.name}")

    choice = input(f"Select a server to delete (1-{len(servers)}): ")

    try:
        choice = int(choice)
        if 1 <= choice <= len(servers):
            server_to_delete = servers[choice - 1]

            # Ensure that the server has an ID
            if not server_to_delete.id:
                print("Server ID not found, cannot delete the server.")
                return

            # Log the server's ID and status
            print(f"Attempting to delete server: {server_to_delete.name} (ID: {server_to_delete.id})")
            print(f"Server status: {server_to_delete.status}")

            # Ask for user confirmation
            confirm = input(f"\nAre you sure you want to delete server '{server_to_delete.name}'? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Server deletion canceled.")
                return

            # Get the security groups attached to the server
            security_groups = server_to_delete.security_groups
            
            # Fetch floating IPs associated with the server
            floating_ips = list(conn.network.ips())
            server_floating_ips = [ip for ip in floating_ips if ip.port_id in [port.id for port in conn.network.ports(device_id=server_to_delete.id)]]

            # Detach floating IPs from the server
            for floating_ip in server_floating_ips:
                try:
                    conn.network.update_ip(floating_ip.id, port_id=None)
                    print(f"\nCleaning up....")
                except Exception as e:
                    print(f"Error detaching floating IP {floating_ip.floating_ip_address}: {e}")

            # Delete floating IPs
            for floating_ip in server_floating_ips:
                try:
                    conn.network.delete_ip(floating_ip.id)
                    print("\n**********************************************************")
                    print(f"Deleted floating IP: {floating_ip.floating_ip_address}")
                except Exception as e:
                    print(f"Error deleting floating IP {floating_ip.floating_ip_address}: {e}")
                    

            # Delete the server
            try:
                conn.compute.delete_server(server_to_delete.id)
                time.sleep(5)  # Give it some time to process the deletion
                print(f"Deleted server: {server_to_delete.name}")
            except Exception as e:
                print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                print(f"Error deleting server: {e}")
                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                
        # Delete non-default security groups
            for sec_group in security_groups:
                sec_group_name = sec_group.get('name') if isinstance(sec_group, dict) else getattr(sec_group, 'name', 'Unknown Name')
                if sec_group_name != "default":
                    try:
                        sec_groups = list(conn.network.security_groups())
                        for sg in sec_groups:
                            if sg.name == sec_group_name:
                                # Remove all rules from the security group
                                rules = list(conn.network.security_group_rules(security_group_id=sg.id))
                                for rule in rules:
                                    conn.network.delete_security_group_rule(rule.id)

                                # Delete the security group
                                conn.network.delete_security_group(sg.id)
                                print(f"Deleted security group: {sec_group_name}")
                                print("**********************************************************")
                    except Exception as e:
                        print(f"Error deleting security group {sec_group_name}: {e}")
        else:
            print("Invalid choice. Please select a valid server.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print(f"Error: {e}")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")



def list_servers(conn):
    print("\n**********************************************************")
    print("List of Servers:")
    servers = conn.compute.servers()
    for i, server in enumerate(servers, start=1):
        print(f"{i}. {server.name}")
    print("**********************************************************")

