import sys
import time

def virtual_routers(conn):
    while True:
        print("\nVirtual Router menu")
        print("1. Create")
        print("2. Delete")
        print("3. Connect")
        print("4. List")
        print("5. Main menu")
        choice = input("Select an option (1-4) or type 'exit': ")

        if choice == "1":
            create(conn)
        elif choice == "2":
            delete(conn)
        elif choice == "3":
            connect_sep(conn)
        elif choice == "4":
            list_routers(conn)
        elif choice == "5":
            print("Returning to main menu...")
            break
        elif choice == "exit":
            print("Exiting application....")
            sys.exit(0)

def create(conn):
    try:
        num_routers = int(input("\nEnter the number of virtual routers to create: "))

        created_routers = []
        for i in range(num_routers):
            r_name = input(f"Enter name for router {i+1}: ")

            # Create router
            router = conn.network.create_router(name=r_name)

            created_routers.append(router)
            print("\n**********************************************************")
            print(f"Created router {router.name}")
            print("**********************************************************")

            # Ask if the user wants to connect to the gateway first
            connect_to_gateway = input("\nDo you want to connect this router to the gateway first? (yes/no): ").strip().lower()
            if connect_to_gateway == "yes":
                public_network = get_public_network(conn)
                if public_network:
                    conn.network.update_router(router, external_gateway_info={"network_id": public_network.id})
                    print("\n**********************************************************")
                    print(f"Connected router {router.name} to the gateway {public_network.name}")
                    print("**********************************************************")
                else:
                    print("No public network found. Skipping gateway connection.")

            # Connect networks to the router
            connect(conn, router)

        return created_routers
    except Exception as e:
        print(f"Error creating routers: {e}")

def get_public_network(conn):
    networks = list(conn.network.networks())
    for network in networks:
        if "public" in network.name.lower():
            return network
    return None


def connect(conn, router):
    try:
        num_subnets = int(input("\nEnter the number of subnets to connect this router to: "))

        subnets = list(conn.network.subnets())
        if not subnets:
            print("No available subnets found.")
            return

        for i in range(num_subnets):
            print("\nAvailable Subnets:")
            for j, subnet in enumerate(subnets, start=1):
                #print(f"{j}. {subnet.name} ({subnet.id}) - Network: {subnet.network_id}")
                print(f"{j}. {subnet.name} ({subnet.id})")

            try:
                subnet_choice = int(input(f"Select subnet {i+1} to connect (1-{len(subnets)}): "))
                if 1 <= subnet_choice <= len(subnets):
                    subnet_to_connect = subnets[subnet_choice - 1]
                else:
                    print("Invalid choice. Skipping this subnet.")
                    continue
            except ValueError:
                print("Invalid input. Skipping this subnet.")
                continue

            # Ensure subnet ID is valid
            if not subnet_to_connect.id:
                print(f"Invalid subnet ID for {subnet_to_connect.name}. Skipping.")
                continue

            print(f"\nConnecting router {router.id} to subnet {subnet_to_connect.id}...")
            conn.network.add_interface_to_router(router.id, subnet_id=subnet_to_connect.id)
            print("\n**********************************************************")
            print(f"Connected subnet {subnet_to_connect.name} to router {router.name}")
            print("**********************************************************")

        return
    except Exception as e:
        print(f"Error connecting subnets: {e}")
        
        
def connect_sep(conn):
    try:
        # Step 1: List routers and let the user select one
        routers = list(conn.network.routers())
        if not routers:
            print("No routers found.")
            return
        
        print("\nAvailable Routers:")
        for i, router in enumerate(routers, start=1):
            print(f"{i}. {router.name} ({router.id})")

        try:
            router_choice = int(input(f"Select a router to connect (1-{len(routers)}): "))
            if 1 <= router_choice <= len(routers):
                router = routers[router_choice - 1]
            else:
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid input.")
            return

        # Step 2: List available subnets and let the user select one or more
        subnets = list(conn.network.subnets())
        if not subnets:
            print("No available subnets found.")
            return

        print("\nAvailable Subnets:")
        for j, subnet in enumerate(subnets, start=1):
            print(f"{j}. {subnet.name} ({subnet.id}) - Network: {subnet.network_id}")

        try:
            num_subnets = int(input("\nHow many subnets do you want to connect this router to? "))
            for _ in range(num_subnets):
                subnet_choice = int(input(f"Select a subnet (1-{len(subnets)}): "))
                if 1 <= subnet_choice <= len(subnets):
                    subnet_to_connect = subnets[subnet_choice - 1]
                else:
                    print("Invalid choice. Skipping this subnet.")
                    continue

                # Ensure subnet ID is valid
                if not subnet_to_connect.id:
                    print(f"Invalid subnet ID for {subnet_to_connect.name}. Skipping.")
                    continue

                print(f"\nConnecting router {router.id} to subnet {subnet_to_connect.id}...")
                conn.network.add_interface_to_router(router.id, subnet_id=subnet_to_connect.id)
                print("\n**********************************************************")
                print(f"Connected {subnet_to_connect.name} to {router.name}")
                print("**********************************************************")

        except ValueError:
            print("Invalid input. Skipping subnet selection.")

    except Exception as e:
        print(f"Error connecting subnets: {e}")


def get_public_network(conn):
    networks = list(conn.network.networks())
    for network in networks:
        if network.name.lower() == "public":
            return network
    return None


def delete(conn):
    print("\nSelect the router you want to delete:")
    routers = list(conn.network.routers())
    if not routers:
        print("No routers found.")
        return

    for i, router in enumerate(routers, start=1):
        print(f"{i}. {router.name}")

    try:
        choice = int(input(f"Select a router to delete (1-{len(routers)}): "))
        if 1 <= choice <= len(routers):
            router_to_delete = routers[choice - 1]

            # Ask for user confirmation
            confirm = input(f"\nAre you sure you want to delete router '{router_to_delete.name}'? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Router deletion canceled.")
                return

            print(f"\nDeleting router: {router_to_delete.name}...")

            # Step 1: Remove the gateway
            if hasattr(router_to_delete, 'external_gateway_info') and router_to_delete.external_gateway_info:
                print(f"Removing gateway from router {router_to_delete.name}...")
                conn.network.remove_gateway_from_router(router_to_delete.id)
                print("\n**********************************************************")
                print(f"Gateway removed from {router_to_delete.name}")
                print("**********************************************************")

                # Wait 5 seconds for OpenStack to handle any automatic detachments
                time.sleep(5)
            else:
                print(f"No gateway found for router {router_to_delete.name}, skipping gateway removal.")

            # Step 2: Get all interfaces currently attached to the router
            attached_ports = list(conn.network.ports(device_id=router_to_delete.id))
            attached_subnets = {p.fixed_ips[0].get('subnet_id') for p in attached_ports if p.fixed_ips}

            # Step 3: Only detach interfaces that are actually attached
            for subnet_id in attached_subnets:
                try:
                    conn.network.remove_interface_from_router(router_to_delete.id, subnet_id=subnet_id)
                    print(f"Detached subnet {subnet_id} from router {router_to_delete.name}")
                except Exception as e:
                    print(f"\nSkipping subnet {subnet_id}, it is already removed while clearing the gateway")

            # Step 4: Delete the router
            conn.network.delete_router(router_to_delete.id)
            print("\n**********************************************************")
            print(f"Deleted router: {router_to_delete.name}")
            print("**********************************************************")

        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error deleting router: {e}")


def list_routers(conn):
    print("\n**********************************************************")
    print("List of Routers:")
    routers = list(conn.network.routers())
    if not routers:
        print("No routers found.")
        return
    for i, router in enumerate(routers, start=1):
        print(f"{i}. {router.name}")
    print("**********************************************************")
