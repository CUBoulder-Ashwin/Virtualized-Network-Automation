import sys
def virtual_networks(conn):
    while True:
        print("\nVirtual Networks menu")
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
            list_networks(conn)
        elif choice == "4":
            print("Returning to main menu...")
            break
        elif choice == "exit":
            print("Exiting application....")
            sys.exit(0)


def create(conn):
    try:
        num_networks = int(input("\nEnter the number of virtual networks to create: "))

        created_networks = []
        for i in range(num_networks):
            net_name = input(f"Enter name for network {i+1}: ")
            subnet_cidr = input(f"Enter CIDR for {net_name} (e.g., 192.168.1.0/24): ")

            # Create network
            network = conn.network.create_network(name=net_name)

            # Create subnet
            subnet = conn.network.create_subnet(
                name=f"{net_name}-subnet",
                network_id=network.id,
                ip_version=4,
                cidr=subnet_cidr,
            )

            created_networks.append(network)
            print("\n**********************************************************")
            print(f"Created network {network.name} with subnet {subnet.cidr}")
            print("**********************************************************")

        return created_networks

    except Exception as e:
        print(f"Error creating networks: {e}")

def delete(conn):
    # Implement network deletion logic here
    print("\nSelect the network you want to delete:")
    networks = list(conn.network.networks())  # Convert generator to list
    for i, network in enumerate(networks, start=1):
        print(f"{i}. {network.name}")

    choice = input(f"Select a network to delete (1-{len(networks)}): ")

    try:
        choice = int(choice)
        if 1 <= choice <= len(networks):
            network_to_delete = networks[choice - 1]
            
            # Ask for user confirmation
            confirm = input(f"\nAre you sure you want to delete network '{network_to_delete.name}'? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Network deletion canceled.")
                return
            
            conn.network.delete_network(network_to_delete.id)
            print("\n**********************************************************")
            print(f"Deleted network: {network_to_delete.name}")
            print("**********************************************************")
        else:
            print("Invalid choice. Please select a valid network number.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print(f"Error deleting network: {e}. Delete any server or router connected before deleting the network")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")



def list_networks(conn):
    print("\n**********************************************************")
    print("List of Networks:")
    networks = conn.network.networks()
    for i, network in enumerate(networks, start=1):
        print(f"{i}. {network.name}")
    print("**********************************************************")
