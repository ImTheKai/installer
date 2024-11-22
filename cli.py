import logging
import subprocess
import json
from shared import SUPPORTED_DISTROS, REPO_TYPES, build_repo_command, ensure_percona_release, detect_os, get_available_solutions, load_solutions_functions
from fetch_versions import fetch_all_versions

logger = logging.getLogger(__name__)

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

def enable_repository(distribution, version, repo_type):
    """
    Enable the repository for the selected distribution, version, and type.
    """
    try:
        # Ensure percona-release is installed
        ensure_percona_release(print)  # Pass print as the callback

        # Build and execute the repository enable command
        command = build_repo_command(distribution, version, repo_type)
        logger.info(f"Enabling repository with command: {command}")
        subprocess.run(command, shell=True, check=True)
        print("Repository enabled successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error enabling repository: {str(e)}")
        print(f"Failed to enable repository: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")

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
        ensure_percona_release(print)  # Ensure percona-release is installed before installation
        pkg_manager = detect_os()
        if not pkg_manager:
            raise Exception("Unable to determine the package manager for your OS.")

        command = f"sudo {pkg_manager} install -y " + " ".join(selected_components)
        logger.info(f"Installing components with command: {command}")
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
            "ppg": "Percona Distribution for PostgreSQL"  # Ensure ppg is mapped
        }

        distribution = PREFIX_TO_DISTRO.get(prefix)
        if not distribution:
            print(f"Error: Invalid distribution prefix '{prefix}'.")
            return

        repo_type = args.get("repository")
        if not repo_type or repo_type not in REPO_TYPES:
            print(f"Error: Repository type is required and must be one of {REPO_TYPES}.")
            return

        components = args.get("components", "").split(",") if args.get("components") else []
        
        solution = args.get("solution")
        if solution:
            # Get the list of available solutions
            available_solutions = get_available_solutions()

            # Check if the parsed solution exists
            if solution not in available_solutions:
                print(f"Solution '{solution}' is not available. Available solutions are:")
                print(", ".join(available_solutions))
                return
            else:
                solution_functions = load_solutions_functions('solution')

        if args.get("verbose"):
            logger.setLevel(logging.DEBUG)
            print("Verbose mode enabled.")
        
        print(f"Selected Distribution: {distribution}")
        print(f"Selected Version: {version}")
        print(f"Selected Repository Type: {repo_type}")
        print(f"Selected Components: {', '.join(components) if components else 'None'}")
        print(f"Selected Solution: {solution}")

        enable_repository(distribution, version, repo_type)
        if components:
            install_components(components)
        if solution:
            pkg_manager = detect_os()
            solution_functions[solution](pkg_manager)
    else:
        # Interactive mode
        print("Welcome to the Percona Installer (CLI Mode)")
        list_distributions()
        distro_index = int(input("Select a distribution: ")) - 1
        distribution = list(SUPPORTED_DISTROS.keys())[distro_index]
        version = select_version(distribution)
        repo_type = select_repo_type()
        enable_repository(distribution, version, repo_type)
        components = list_components(distribution, version)
        selected_components = select_components(components)
        if components:
            install_components(selected_components)
