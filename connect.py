import subprocess
import os


def source_openrc():
    """Sources openrc.sh to set OpenStack environment variables."""
    try:
        command = "bash -c 'source openrc.sh && env'"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, executable="/bin/bash"
        )

        if result.returncode == 0:
            for line in result.stdout.splitlines():
                key, _, value = line.partition("=")
                os.environ[key] = value
        else:
            print("Failed to source openrc.sh:", result.stderr)

    except Exception as e:
        print(f"Error sourcing openrc.sh: {e}")


def get_connection():
    """Establish OpenStack connection after sourcing environment variables."""
    source_openrc()

    import openstack

    try:
        conn = openstack.connect()
        print("Successfully connected to OpenStack.")
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None