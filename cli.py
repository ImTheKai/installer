import logging
import json
import subprocess
from fetch_versions import fetch_all_versions

# Configure logging
logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

SUPPORTED_DISTROS = {
    "Percona Server for MySQL": "pdps-",
    "Percona Distribution for MySQL (PXC)": "pdpxc-",
    "Percona Distribution for MongoDB": "pdmdb-",
    "Percona Distribution for PostgreSQL": "ppg-"
}

REPO_TYPES = ["release", "testing", "experimental"]

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
                raise Exception("Unsupported Linux distribution detected in /etc/os-release.")

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

def list_distributions():
    """
    Display available distributions.
    """
    print("Available Distributions:")
    for i, distro in enumerate(SUPPORTED_DISTROS.keys(), start=1):
        print(f"{i}. {distro}")

def select_version(distribution):
    """
    Fetch and display versions for a selected distribution, and allow the user to select one.
    """
    prefix = SUPPORTED_DISTROS[distribution]
    try:
        all_versions = fetch_all_versions(prefix)
        if not all_versions:
            print("No versions available for the selected distribution.")
            return None

        print("Available Versions:")
        for i, version in enumerate(all_versions, start=1):
            print(f"{i}. {version}")

        version_index = int(input("Select a version: ")) - 1
        if 0 <= version_index < len(all_versions):
            return all_versions[version_index]
        else:
            print("Invalid selection.")
            return None
    except Exception as e:
        logger.error(f"Error fetching versions for {distribution}: {str(e)}")
        print(f"Error fetching versions: {str(e)}")
        return None

def select_repo_type():
    """
    Display repository types and allow the user to select one.
    """
    print("Available Repository Types:")
    for i, repo_type in enumerate(REPO_TYPES, start=1):
        print(f"{i}. {repo_type}")

    repo_index = int(input("Select a repository type: ")) - 1
    if 0 <= repo_index < len(REPO_TYPES):
        return REPO_TYPES[repo_index]
    else:
        print("Invalid selection.")
        return None

def enable_repository(distribution, version, repo_type):
    """
    Enable the repository for the selected distribution, version, and type.
    """
    try:
        repo_name = f"{SUPPORTED_DISTROS[distribution]}{version}"
        command = f"sudo percona-release enable {repo_name} {repo_type}"
        logger.info(f"Enabling repository with command: {command}")
        subprocess.run(command, shell=True, check=True)
        print("Repository enabled successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error enabling repository: {str(e)}")
        print(f"Failed to enable repository: {str(e)}")

def list_components(distribution, version):
    """
    Load and display components for the selected distribution and version.
    """
    try:
        with open("components.json", "r") as file:
            components_data = json.load(file)
            components = components_data.get(distribution, {}).get("components", [])

            # Replace {major} placeholder with major version
            major_version = version.split(".")[0]
            components = [
                component.replace("{major}", major_version) if "{major}" in component else component
                for component in components
            ]

            if not components:
                print("No components available for the selected distribution.")
                return None

            print("Available Components:")
            for i, component in enumerate(components, start=1):
                print(f"{i}. {component}")
            return components
    except FileNotFoundError:
        logger.error("components.json file is missing!")
        print("Error: components.json not found.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing components.json: {str(e)}")
        print("Error: Failed to parse components.json.")
        return None

def select_components(components):
    """
    Allow the user to select components for installation.
    """
    print("Select components to install (comma-separated, e.g., 1,3,5):")
    selection = input("Enter your selection: ")
    selected_indices = [int(index.strip()) - 1 for index in selection.split(",") if index.strip().isdigit()]
    selected_components = [components[i] for i in selected_indices if 0 <= i < len(components)]
    return selected_components

def install_components(selected_components):
    """
    Build and execute the install command for the selected components.
    """
    if not selected_components:
        print("No components selected for installation.")
        return

    try:
        pkg_manager = detect_os()
        command = f"sudo {pkg_manager} install -y " + " ".join(selected_components)
        logger.info(f"Installing components with command: {command}")
        print(f"Executing: {command}")
        subprocess.run(command, shell=True, check=True)
        print("Components installed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing components: {str(e)}")
        print(f"Failed to install components: {str(e)}")

def run_cli():
    """
    Run the CLI installer.
    """
    print("Welcome to the Percona Installer (CLI Mode)")

    list_distributions()
    distro_index = int(input("Select a distribution: ")) - 1
    if not (0 <= distro_index < len(SUPPORTED_DISTROS)):
        print("Invalid distribution selection.")
        return

    distribution = list(SUPPORTED_DISTROS.keys())[distro_index]
    version = select_version(distribution)
    if not version:
        return

    repo_type = select_repo_type()
    if not repo_type:
        return

    enable_repository(distribution, version, repo_type)

    components = list_components(distribution, version)
    if not components:
        return

    selected_components = select_components(components)
    install_components(selected_components)
