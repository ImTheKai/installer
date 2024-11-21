
import npyscreen
from shared import SUPPORTED_DISTROS, REPO_TYPES, detect_os, build_repo_command, ensure_percona_release
import logging
import json
import subprocess

logger = logging.getLogger(__name__)

class InstallerApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Percona Installer")
        self.addForm("REPO_SETUP", RepoSetupForm, name="Setup Repository")
        self.addForm("COMPONENTS", ComponentSelectionForm, name="Select Components")

class MainForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleText, name="Welcome to Percona Installer!")

        self.distro = self.add(
            npyscreen.TitleSelectOne,
            max_height=5,
            name="Select Distribution",
            values=list(SUPPORTED_DISTROS.keys()),
            scroll_exit=True
        )
        self.distro.when_value_edited = self.on_distro_change

        self.version = self.add(
            npyscreen.TitleSelectOne,
            max_height=8,
            name="Select Version",
            values=["Select a distribution first"],
            scroll_exit=True
        )

        self.next_button = self.add(npyscreen.ButtonPress, name="Next")
        self.next_button.whenPressed = self.next_screen

        self.exit_button = self.add(npyscreen.ButtonPress, name="Exit")
        self.exit_button.whenPressed = self.exit_program

    def afterEditing(self):
        pass  # Suppress default OK behavior

    def on_distro_change(self):
        self.update_versions()

    def update_versions(self):
        selected_distro = self.distro.get_selected_objects()
        if not selected_distro:
            self.version.values = ["Select a distribution first"]
            self.display()
            return

        prefix = SUPPORTED_DISTROS[selected_distro[0]]
        try:
            from fetch_versions import fetch_all_versions
            all_versions = fetch_all_versions(prefix)
            self.version.values = all_versions if all_versions else ["No versions available"]
            self.version.value = 0 if all_versions else None
        except Exception as e:
            self.version.values = [f"Error fetching versions: {str(e)}"]
            self.version.value = None

        self.display()

    def next_screen(self):
        selected_distro = self.distro.get_selected_objects()
        selected_version = self.version.get_selected_objects()

        if not selected_distro or not selected_version:
            npyscreen.notify_confirm("Please select a distribution and version first.", title="Error")
            return

        repo_form = self.parentApp.getForm("REPO_SETUP")
        repo_form.setup(selected_distro[0], selected_version[0])
        self.parentApp.switchForm("REPO_SETUP")

    def exit_program(self):
        npyscreen.notify_confirm("Exiting the installer. Goodbye!", title="Exit")
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

class RepoSetupForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleText, name="Setup Repository:")

        self.repo_type = self.add(
            npyscreen.TitleSelectOne,
            max_height=5,
            name="Select Repository Type",
            values=REPO_TYPES,
            scroll_exit=False
        )

        self.install_percona_button = self.add(npyscreen.ButtonPress, name="Install percona-release")
        self.install_percona_button.whenPressed = self.install_percona_release

        self.enable_repo_button = self.add(npyscreen.ButtonPress, name="Enable Repository")
        self.enable_repo_button.whenPressed = self.enable_repository

        self.next_button = self.add(npyscreen.ButtonPress, name="Next")
        self.next_button.whenPressed = self.next_screen

        self.back_button = self.add(npyscreen.ButtonPress, name="Back")
        self.back_button.whenPressed = self.back_to_main

        self.exit_button = self.add(npyscreen.ButtonPress, name="Exit")
        self.exit_button.whenPressed = self.exit_program

    def install_percona_release(self):
        """
        Install the percona-release package using shared.ensure_percona_release.
        """
        def gui_output_callback(message):
            npyscreen.notify_wait(message.strip())

        try:
            ensure_percona_release(gui_output_callback)
        except Exception as e:
            npyscreen.notify_confirm(f"Failed to install percona-release: {str(e)}", title="Error")
            logger.error(f"Error installing percona-release: {str(e)}")

    def enable_repository(self):
        """
        Enable the selected repository using percona-release.
        """
        selected_repo_type = self.repo_type.get_selected_objects()

        if not selected_repo_type:
            npyscreen.notify_confirm("Please select a repository type first.", title="Error")
            return

        try:
            repo_command = build_repo_command(self.selected_distro, self.selected_version, selected_repo_type[0])
            subprocess.run(repo_command, shell=True, check=True)
            npyscreen.notify_confirm("Repository enabled successfully!", title="Success")
        except subprocess.CalledProcessError as e:
            npyscreen.notify_confirm(f"Failed to enable repository: {str(e)}", title="Error")
            logger.error(f"Error enabling repository: {str(e)}")
    def setup(self, distribution, version):
        self.selected_distro = distribution
        self.selected_version = version
        logger.debug(f"RepoSetupForm initialized with distro: {distribution}, version: {version}")

    def next_screen(self):
        components_form = self.parentApp.getForm("COMPONENTS")
        components_form.setup(self.selected_distro, self.selected_version)
        self.parentApp.switchForm("COMPONENTS")

    def back_to_main(self):
        self.parentApp.switchForm("MAIN")

    def exit_program(self):
        npyscreen.notify_confirm("Exiting the installer. Goodbye!", title="Exit")
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

class ComponentSelectionForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleText, name="Select Components for Installation:")

        self.components = self.add(
            npyscreen.MultiSelect,
            max_height=10,
            values=["Select components after enabling repository"],
            scroll_exit=True
        )

        self.install_button = self.add(npyscreen.ButtonPress, name="Install")
        self.install_button.whenPressed = self.install_components

        self.back_button = self.add(npyscreen.ButtonPress, name="Back")
        self.back_button.whenPressed = self.back_to_repo_setup

        self.exit_button = self.add(npyscreen.ButtonPress, name="Exit")
        self.exit_button.whenPressed = self.exit_program

    def setup(self, distribution, version):
        self.selected_distro = distribution
        self.selected_version = version
        major_version = version.split(".")[0]
        try:
            with open("components.json", "r") as file:
                components_data = json.load(file)
                components = components_data.get(distribution, {}).get("components", [])
                components = [
                    component.replace("{major}", major_version) if "{major}" in component else component
                    for component in components
                ]
                self.components.values = components if components else ["No components available"]
        except FileNotFoundError:
            self.components.values = ["Error: components.json not found"]
        except json.JSONDecodeError as e:
            self.components.values = ["Error: Failed to parse components.json"]

        self.display()

    def install_components(self):
        selected_components = [self.components.values[i] for i in self.components.value]
        if not selected_components:
            npyscreen.notify_confirm("No components selected for installation.", title="Error")
            return

        try:
            install_command = self.build_install_command(selected_components)
            npyscreen.notify_confirm(f"Installation command: {install_command}", title="Installation")
        except Exception as e:
            npyscreen.notify_confirm(f"Error: {str(e)}", title="Installation Error")

    def build_install_command(self, selected_components):
        pkg_manager = detect_os()
        return f"sudo {pkg_manager} install -y " + " ".join(selected_components)

    def back_to_repo_setup(self):
        self.parentApp.switchForm("REPO_SETUP")

    def exit_program(self):
        npyscreen.notify_confirm("Exiting the installer. Goodbye!", title="Exit")
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

def run_gui():
    logger.info("Starting the GUI application.")
    app = InstallerApp()
    app.run()
    logger.info("GUI application terminated.")

