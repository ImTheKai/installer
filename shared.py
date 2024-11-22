import logging
import os
import platform
import subprocess
import json

# Configure logging
logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Shared constants
SUPPORTED_DISTROS = {
    "Percona Server for MySQL": "pdps-",
    "Percona Distribution for MySQL (PXC)": "pdpxc-",
    "Percona Distribution for MongoDB": "pdmdb-",
    "Percona Distribution for PostgreSQL": "ppg-"
}

REPO_TYPES = ["main", "testing", "experimental"]

# Shared functions
def detect_os():
    """
    Detect the operating system and return the appropriate package manager.
    Supports popular Linux distributions like Ubuntu, Debian, CentOS, Rocky, AlmaLinux, Fedora, etc.
    """
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as file:
                os_release = file.read().lower()

            if "ubuntu" in os_release or "debian" in os_release:
                return "apt-get"
            elif "centos" in os_release or "red hat" in os_release or "rocky" in os_release or "alma" in os_release:
                return "yum"
            elif "fedora" in os_release:
                return "dnf"
            else:
                raise Exception("Unsupported Linux distribution detected.")

        os_id = platform.system().lower()
        if os_id == "linux":
            raise Exception("Minimal Linux distribution detected. Unable to determine package manager.")
        elif os_id == "windows":
            raise Exception("Windows is not supported.")
        elif os_id == "darwin":
            raise Exception("MacOS is not supported.")
        else:
            raise Exception("Unsupported operating system.")

    except Exception as e:
        logger.error(f"Error detecting OS: {str(e)}")
        raise Exception(f"Unsupported OS: {str(e)}")

def ensure_percona_release(output_callback):
    """
    Ensures the Percona Release package is downloaded and installed.
    Provides real-time feedback via the provided callback.
    """
    try:
        output_callback("Ensuring Percona Release package is installed...\n")

        # Check if the percona-release command exists
        result = subprocess.run(
            ["which", "percona-release"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        if result.returncode == 0:
            output_callback("percona-release is already installed.\n")
            logger.info("percona-release is already installed.")
            return

        # Detect the host OS
        package_manager = detect_os()

        if package_manager == "apt-get":
            # Update package list
            output_callback("Updating package list...\n")
            subprocess.run(["sudo", "apt-get", "update"], check=True)

            # Install wget if not present
            output_callback("Checking for wget...\n")
            subprocess.run(["sudo", "apt-get", "install", "-y", "wget"], check=True)

            # Get the codename of the OS
            output_callback("Determining OS codename...\n")
            codename = subprocess.check_output(["lsb_release", "-sc"], text=True).strip()

            # Check if the Percona Release package is already downloaded
            packagename = f"percona-release_latest.{codename}_all.deb"
            if not os.path.exists(packagename):
                output_callback("Downloading Percona Release package...\n")
                url = f"https://repo.percona.com/apt/percona-release_latest.{codename}_all.deb"
                subprocess.run(["wget", url], check=True)
            else:
                output_callback("Percona Release package already downloaded.\n")

            # Install the downloaded package
            output_callback("Installing Percona Release package...\n")
            subprocess.run(["sudo", "dpkg", "-i", packagename], check=True)

            # Update package list again
            output_callback("Updating package list after installation...\n")
            subprocess.run(["sudo", "apt-get", "update"], check=True)

        elif package_manager in ["yum", "dnf"]:
            # Install the percona-release package
            output_callback("Installing Percona Release package...\n")
            subprocess.run(["sudo", package_manager, "install", "-y", "https://repo.percona.com/yum/percona-release-latest.noarch.rpm"], check=True)

            # Enable the Percona repository
            output_callback("Enabling Percona repository...\n")
            subprocess.run(["sudo", "percona-release", "enable", "original"], check=True)

            # Update package list
            output_callback("Updating package list...\n")
            subprocess.run(["sudo", package_manager, "update"], check=True)

        else:
            output_callback(f"Unsupported package manager: {package_manager}\n")
            return

        output_callback("Percona Release package successfully installed.\n")
    except subprocess.CalledProcessError as e:
        output_callback(f"Error during installation: {str(e)}\n")
    except Exception as e:
        output_callback(f"Unexpected error: {str(e)}\n")

# New Shared Utilities

def build_repo_command(distribution, version, repo_type):
    """
    Build the repository enable command.

    Args:
        distribution (str): The selected distribution.
        version (str): The selected version.
        repo_type (str): The repository type.

    Returns:
        str: The constructed command.
    """
    repo_name = f"{SUPPORTED_DISTROS[distribution]}{version}"
    return f"sudo percona-release enable {repo_name} {repo_type}"


def display_options(options, header="Options"):
    """
    Display a list of options to the user.

    Args:
        options (list): The list of options to display.
        header (str): The header for the display.

    Returns:
        None
    """
    print(header + ":")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")


# Platform Constants
SUPPORTED_PLATFORMS = {
    "Ubuntu": ["20.04", "22.04", "24.04"],
    "Debian": ["11", "12"],
    "Oracle Linux": ["8", "9"],
    "Rocky Linux": ["8", "9"],
    "AlmaLinux": ["8", "9"]
}

NORMALIZED_DISTROS = {
    "oracle linux server": "Oracle Linux",
    "oracle linux": "Oracle Linux",
    "ubuntu": "Ubuntu",
    "debian": "Debian",
    "rocky": "Rocky Linux",
    "almalinux": "AlmaLinux"
}
