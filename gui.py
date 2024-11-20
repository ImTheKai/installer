import npyscreen
import logging
import json
import platform
import os

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

class InstallerApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Percona Installer")
        self.addForm("COMPONENTS", ComponentSelectionForm, name="Select Components")


class MainForm(npyscreen.Form):
    def create(self):
        # Welcome Message
        self.add(npyscreen.TitleText, name="Welcome to Percona Installer!")

        # Distribution Selection
        self.distro = self.add(
            npyscreen.TitleSelectOne,
            max_height=5,
            name="Select Distribution",
            values=list(SUPPORTED_DISTROS.keys()),
            scroll_exit=True
        )
        self.distro.when_value_edited = self.on_distro_change

        # Version Selection
        self.version = self.add(
            npyscreen.TitleSelectOne,
            max_height=8,
            name="Select Version",
            values=["Select a distribution first"],
            scroll_exit=True
        )

        # Next and Exit Buttons
        self.next_button = self.add(npyscreen.ButtonPress, name="Next")
        self.next_button.whenPressed = self.next_screen

        self.exit_button = self.add(npyscreen.ButtonPress, name="Exit")
        self.exit_button.whenPressed = self.exit_program

    def on_distro_change(self):
        """Trigger version fetching when the distribution changes."""
        logger.debug("Distribution selection changed.")
        self.update_versions()

    def update_versions(self):
        """Update the version list based on the selected distribution."""
        selected_distro = self.distro.get_selected_objects()
        if not selected_distro:
            logger.debug("No distribution selected yet.")
            self.version.values = ["Select a distribution first"]
            self.display()
            return  # No selection made yet

        # Debugging: Log selected distribution
        logger.debug(f"Selected distribution: {selected_distro[0]}")

        prefix = SUPPORTED_DISTROS[selected_distro[0]]
        try:
            logger.debug(f"Fetching versions for prefix: {prefix}")
            # Call the fetch_all_versions function here
            from fetch_versions import fetch_all_versions
            all_versions = fetch_all_versions(prefix)
            logger.debug(f"Fetched versions for {selected_distro[0]}: {all_versions}")

            if all_versions:
                self.version.values = all_versions
                self.version.value = 0  # Default to the first option
                logger.debug(f"Updated version values: {self.version.values}")
            else:
                self.version.values = ["No versions available"]
                self.version.value = None
                logger.debug("No versions available.")
        except Exception as e:
            logger.error(f"Error fetching versions for {selected_distro[0]}: {str(e)}")
            self.version.values = [f"Error fetching versions: {str(e)}"]
            self.version.value = None

        self.display()

    def next_screen(self):
        """Move to the component selection screen."""
        selected_distro = self.distro.get_selected_objects()
        selected_version = self.version.get_selected_objects()

        if not selected_distro or not selected_version:
            npyscreen.notify_confirm("Please select a distribution and version first.", title="Error")
            return

        # Pass selection to the ComponentSelectionForm
        self.parentApp.getForm("COMPONENTS").setup(selected_distro[0], selected_version[0])
        self.parentApp.switchForm("COMPONENTS")

    def exit_program(self):
        """Exit the program."""
        logger.info("Exiting the installer.")
        npyscreen.notify_confirm("Exiting the installer. Goodbye!", title="Exit")
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

class ComponentSelectionForm(npyscreen.Form):
    def create(self):
        # Title
        self.add(npyscreen.TitleText, name="Select Components for Installation:")

        # Components List
        self.components = self.add(
            npyscreen.MultiSelect,
            max_height=10,
            values=["Select components after choosing a distribution"],
            scroll_exit=True
        )

        # Install and Back Buttons
        self.install_button = self.add(npyscreen.ButtonPress, name="Install")
        self.install_button.whenPressed = self.install_components

        self.back_button = self.add(npyscreen.ButtonPress, name="Back")
        self.back_button.whenPressed = self.back_to_main

    def setup(self, distribution, version):
        """Setup the form with the selected distribution and version."""
        logger.debug(f"Setting up ComponentSelectionForm for distribution: {distribution}, version: {version}")
        self.selected_distro = distribution
        self.selected_version = version

        # Extract major version for PostgreSQL
        major_version = version.split(".")[0]
        logger.debug(f"Extracted major version: {major_version}")

        # Load components for the selected distribution
        try:
            with open("components.json", "r") as file:
                logger.debug("Loading components.json file.")
                components_data = json.load(file)
                logger.debug(f"Contents of components.json: {json.dumps(components_data, indent=2)}")

                # Get components for the selected distribution
                components = components_data.get(distribution, {}).get("components", [])
                logger.debug(f"Components before placeholder replacement: {components}")

                # Replace {major} placeholder in components
                components = [
                    component.replace("{major}", major_version) if "{major}" in component else component
                    for component in components
                ]
                logger.debug(f"Components after placeholder replacement: {components}")

                if components:
                    self.components.values = components
                    logger.debug(f"Loaded components into MultiSelect: {components}")
                else:
                    self.components.values = ["No components available"]
                    logger.warning(f"No components found for distribution: {distribution}")

        except FileNotFoundError:
            self.components.values = ["Error: components.json not found"]
            logger.error("components.json file is missing!")
        except json.JSONDecodeError as e:
            self.components.values = ["Error: Failed to parse components.json"]
            logger.error(f"Error parsing components.json: {str(e)}")

        # Refresh the display
        self.display()

    def install_components(self):
        """Log and execute the installation for selected components."""
        selected_components = [self.components.values[i] for i in self.components.value]
        if not selected_components:
            npyscreen.notify_confirm("No components selected for installation.", title="Error")
            return

        try:
            install_command = self.build_install_command(selected_components)
            logger.info(f"Installing components with command: {install_command}")
            npyscreen.notify_confirm(f"Installation command: {install_command}", title="Installation")
        except Exception as e:
            logger.error(f"Error building installation command: {str(e)}")
            npyscreen.notify_confirm(f"Error: {str(e)}", title="Installation Error")

    def build_install_command(self, selected_components):
        """Build an installation command based on selected components and the OS."""
        pkg_manager = detect_os()
        command = f"sudo {pkg_manager} install -y " + " ".join(selected_components)
        logger.debug(f"Built install command: {command}")
        return command

    def back_to_main(self):
        """Go back to the main form."""
        self.parentApp.switchForm("MAIN")

def run_gui():
    """Run the GUI application."""
    logger.info("Starting the GUI application.")
    app = InstallerApp()
    app.run()
    logger.info("GUI application terminated.")

