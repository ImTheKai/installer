import json
import platform
import os 
import logging
from fetch_versions import fetch_all_versions  # Import the dynamic fetching function

# Configure logging
logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

SUPPORTED_DISTROS = {
    "Percona Server for MySQL": "pdps-",
    "Percona XtraDB Cluster": "pdpxc-",
    "Percona Server for MongoDB": "pdmdb-",
    "Percona Distribution for PostgreSQL": "ppg-"
}

JSON_KEY_MAPPING = {
    "Percona Server for MySQL": "Percona Server for MySQL",
    "Percona XtraDB Cluster": "Percona Distribution for MySQL (PXC)",
    "Percona Server for MongoDB": "Percona Distribution for MongoDB",
    "Percona Distribution for PostgreSQL": "Percona Distribution for PostgreSQL"
}

def detect_os():
    """
    Detect the operating system and return the appropriate package manager.
    Supports popular Linux distributions like Ubuntu, Debian, CentOS, Rocky, AlmaLinux, Fedora, etc.
    """
    try:
        # Check /etc/os-release for detailed OS information
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
                raise Exception("Unsupported Linux distribution detected in /etc/os-release.")

        # Fallback for non-Linux or minimal Linux distributions
        os_id = platform.system().lower()
        if "linux" in os_id:
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

def load_components():
    """Load and parse the components.json file."""
    try:
        with open("components.json", "r") as file:
            components_data = json.load(file)
            logger.debug(f"Loaded components.json: {json.dumps(components_data, indent=2)}")
            return components_data
    except FileNotFoundError:
        logger.error("components.json file is missing!")
        print("Error: components.json file not found.")
        exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing components.json: {str(e)}")
        print("Error: Failed to parse components.json.")
        exit(1)

def run_cli():
    """Run the CLI application."""
    components_data = load_components()

    print("Select the Percona Distribution to install:")
    distributions = list(SUPPORTED_DISTROS.keys())
    for idx, dist in enumerate(distributions, start=1):
        print(f"{idx}. {dist}")

    dist_choice = input("Enter the number corresponding to your choice: ").strip()
    if not dist_choice.isdigit() or int(dist_choice) not in range(1, len(distributions) + 1):
        print("Invalid choice. Exiting.")
        return

    selected_distro = distributions[int(dist_choice) - 1]
    print(f"\nYou selected: {selected_distro}")

    prefix = SUPPORTED_DISTROS[selected_distro]
    try:
        logger.debug(f"Fetching versions for prefix: {prefix}")
        versions = fetch_all_versions(prefix)  # Dynamically fetch versions
        logger.debug(f"Fetched versions for {selected_distro}: {versions}")
    except Exception as e:
        print(f"Error fetching versions: {str(e)}")
        logger.error(f"Error fetching versions for {selected_distro}: {str(e)}")
        return

    if not versions:
        print(f"No versions available for {selected_distro}. Exiting.")
        return

    print("\nAvailable Versions:")
    for idx, version in enumerate(versions, start=1):
        print(f"{idx}. {version}")

    version_choice = input("Enter the number corresponding to the version you want: ").strip()
    if not version_choice.isdigit() or int(version_choice) not in range(1, len(versions) + 1):
        print("Invalid choice. Exiting.")
        return

    selected_version = versions[int(version_choice) - 1]
    print(f"\nYou selected version: {selected_version}")

    # Extract major version for PostgreSQL
    major_version = selected_version.split(".")[0]
    logger.debug(f"Extracted major version: {major_version}")

    json_key = JSON_KEY_MAPPING.get(selected_distro, selected_distro)
    components = components_data.get(json_key, {}).get("components", [])
    if not components:
        print(f"No components available for {selected_distro}. Exiting.")
        return

    # Replace {major} placeholder in components
    components = [
        component.replace("{major}", major_version) if "{major}" in component else component
        for component in components
    ]
    logger.debug(f"Components after placeholder replacement: {components}")

    print("\nAvailable Components:")
    for idx, comp in enumerate(components, start=1):
        print(f"{idx}. {comp}")

    comp_choice = input("Enter the numbers of components to install (comma-separated, e.g., 1,2,3): ").strip()
    selected_components = []
    for num in comp_choice.split(","):
        if num.strip().isdigit() and int(num.strip()) in range(1, len(components) + 1):
            selected_components.append(components[int(num.strip()) - 1])

    if not selected_components:
        print("No components selected. Exiting.")
        return

    print(f"\nSelected components for installation: {', '.join(selected_components)}")

    try:
        pkg_manager = detect_os()
        install_command = f"sudo {pkg_manager} install -y " + " ".join(selected_components)
        print(f"\nInstallation command: {install_command}")
        logger.info(f"Built installation command: {install_command}")
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error building installation command: {str(e)}")
if __name__ == "__main__":
    run_cli()

