import os
import platform
import logging
import subprocess
import json
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

        os_name = platform.system().lower()
        if "linux" in os_name:
            raise Exception("Minimal Linux distribution detected. Unable to determine package manager.")
        elif os_name == "windows":
            raise Exception("Windows is not supported.")
        elif os_name == "darwin":
            raise Exception("MacOS is not supported.")
        else:
            raise Exception("Unsupported operating system.")

    except Exception as e:
        logger.error(f"Error detecting OS: {str(e)}")
        raise Exception(f"Unsupported OS: {str(e)}")

def ensure_percona_release():
    """
    Ensure the 'percona-release' package is installed. If not, download and install it from Percona's repositories.
    """
    PERCONA_RELEASE_URLS = {
        "deb": "https://repo.percona.com/apt/percona-release_1.0-29.generic_all.deb",
        "rpm": "https://repo.percona.com/yum/percona-release-latest.noarch.rpm"
    }

    try:
        # Check if the percona-release command exists
        result = subprocess.run(
            ["which", "percona-release"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True
        )
        if result.returncode == 0:
            print("percona-release is already installed.")
            logger.info("percona-release is already installed.")
            return

        # Detect the package manager
        pkg_manager = detect_os()
        if not pkg_manager:
            raise Exception("Unable to determine package manager for installing percona-release.")

        if pkg_manager == "apt-get":
            # Download and install the .deb package
            percona_release_url = PERCONA_RELEASE_URLS["deb"]
            local_file = "/tmp/percona-release.deb"
            print(f"Downloading {percona_release_url}...")
            logger.info(f"Downloading {percona_release_url}...")
            subprocess.run(["wget", "-O", local_file, percona_release_url], check=True)
            print("Installing percona-release package...")
            logger.info("Installing percona-release package...")
            subprocess.run(["sudo", "apt-get", "install", "-y", local_file], check=True)
            print("percona-release installed successfully.")
            logger.info("percona-release installed successfully.")

        elif pkg_manager in ["yum", "dnf"]:
            # Directly install the .rpm package
            percona_release_url = PERCONA_RELEASE_URLS["rpm"]
            print(f"Installing {percona_release_url} using {pkg_manager}...")
            logger.info(f"Installing {percona_release_url} using {pkg_manager}...")
            subprocess.run(["sudo", pkg_manager, "install", "-y", percona_release_url], check=True)
            print("percona-release installed successfully.")
            logger.info("percona-release installed successfully.")

        else:
            raise Exception(f"Unsupported package manager: {pkg_manager}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing percona-release: {str(e)}")
        print(f"Failed to install percona-release: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        raise

def enable_repository(distribution, version, repo_type):
    """
    Enable the repository for the selected distribution, version, and type.
    """
    try:
        # Ensure percona-release is installed
        ensure_percona_release()

        # Build and execute the repository enable command
        repo_name = f"{SUPPORTED_DISTROS[distribution]}{version}"
        command = f"sudo percona-release enable {repo_name} {repo_type}"
        logger.info(f"Enabling repository with command: {command}")
        subprocess.run(command, shell=True, check=True)
        print("Repository enabled successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error enabling repository: {str(e)}")
        print(f"Failed to enable repository: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")

def list_distributions():
    """
    Display available distributions to the user.
    """
    print("Available Distributions:")
    for i, distro in enumerate(SUPPORTED_DISTROS.keys(), start=1):
        print(f"{i}. {distro}")

def select_version(distribution):
    """
    Fetch and display available versions for a selected distribution, and allow user selection.
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
    Display repository types and allow user selection.
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
        ensure_percona_release()  # Ensure percona-release is installed before any installation
        pkg_manager = detect_os()
        if not pkg_manager:
            raise Exception("Unable to determine the package manager for your OS.")

        command = f"sudo {pkg_manager} install -y " + " ".join(selected_components)
        logger.info(f"Installing components with command: {command}")
        print(f"Executing: {command}")
        subprocess.run(command, shell=True, check=True)
        print("Components installed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing components: {str(e)}")
        print(f"Failed to install components: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")

def run_cli(args=None):
    """
    Run the CLI installer, optionally using provided arguments.
    """
    if args:
        # Argument-driven CLI mode
        product = args.get("product")
        if not product:
            print("Error: Product is required (e.g., ppg-17.0, ps-80).")
            return

        try:
            prefix, version = product.split("-", 1)
        except ValueError:
            print(f"Error: Invalid product format '{product}'. Expected format: <prefix>-<version> (e.g., ppg-17.0).")
            return

        PREFIX_TO_DISTRO = {
            "pdps": "Percona Server for MySQL",
            "pdpxc": "Percona Distribution for MySQL (PXC)",
            "pdmdb": "Percona Distribution for MongoDB",
            "ppg": "Percona Distribution for PostgreSQL"
        }

        distribution = PREFIX_TO_DISTRO.get(prefix)
        if not distribution:
            print(f"Error: Invalid distribution prefix '{prefix}'.")
            return

        repo_type = args.get("repository")
        if not repo_type or repo_type not in REPO_TYPES:
            print(f"Error: Repository type is required and must be one of {REPO_TYPES}.")
            return

        components = args.get("components")
        if components:
            components = components.split(",")  # Split comma-separated components into a list
        else:
            print("Warning: No components specified. Continuing without specific components.")

        verbose = args.get("verbose", False)

        # Enable verbose logging if requested
        if verbose:
            logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()  # Log to console
            console_handler.setLevel(logging.DEBUG)
            logger.addHandler(console_handler)
            print("Verbose mode enabled.")

        print(f"Selected Distribution: {distribution}")
        print(f"Selected Version: {version}")
        print(f"Selected Repository Type: {repo_type}")
        print(f"Selected Components: {', '.join(components) if components else 'None'}")

        # Enable the repository
        print(f"Enabling repository for {distribution} {version} ({repo_type})...")
        enable_repository(distribution, version, repo_type)

        # Install the components if specified
        if components:
            print("Installing selected components...")
            install_components(components)
        else:
            print("No components to install.")
    else:
        # Interactive mode
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
