from connect import get_connection
from network import virtual_networks
from router import virtual_routers
from server import virtual_servers
from security import virtual_sgroups

def main():
    """Create virtual networks based on user input."""
    conn = get_connection()
    if not conn:
        return

    while True:
        print("\nVirtual Networking Automation Main menu")
        print("1. Network")
        print("2. Router")
        print("3. Server")
        print("4. Security Group")
        choice = input("Select an option (1-5) or type 'exit': ")
        if choice == "1":
            virtual_networks(conn)
        elif choice == "2":
            virtual_routers(conn)
        elif choice == "3":
            virtual_servers(conn)
        elif choice == "4":
            virtual_sgroups(conn)
        elif choice == "exit":
            print("Exiting application....")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
