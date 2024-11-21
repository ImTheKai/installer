
# Percona Installer

The **Percona Installer** is a Python-based utility that facilitates the installation of Percona software distributions. It offers an interactive and user-friendly approach for installing popular Percona products like MySQL, PostgreSQL, and MongoDB on supported platforms.

---

## Features

- **Supports multiple Percona distributions**:
  - Percona Server for MySQL
  - Percona XtraDB Cluster (PXC)
  - Percona Distribution for MongoDB
  - Percona Distribution for PostgreSQL
- **Interactive installation process**:
  - Provides an easy-to-use interface for selecting and installing Percona products.
- **Platform detection**:
  - Ensures compatibility by identifying the operating system and distribution.
- **Extensible architecture**:
  - Modular design allows easy updates and customization.

---

## Prerequisites

- Python 3.6 or higher.
- `curses` library (required for GUI mode).
- `git` (for cloning the repository).
- Root or sudo access for installing Percona packages.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EvgeniyPatlan/installer.git
   cd installer
   ```

2. (Optional) Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add the `percona_installer` script to `/usr/bin` for global access:
   ```bash
   sudo cp percona_installer /usr/bin/
   sudo chmod +x /usr/bin/percona_installer
   ```

---

## Usage

### Running the Installer

To execute the installer, run:
```bash
percona_installer
```

The installer provides a step-by-step process for selecting and installing the desired Percona distribution.

### Dockerized Usage

1. Build the Docker image:
   ```bash
   docker build -t percona_installer_image .
   ```

2. Run the container:
   ```bash
   docker run --rm -it percona_installer_image
   ```

---

## Code Overview

The Percona Installer codebase is modular, with each module handling specific functionality. Below is a breakdown of the key files and their core functions:

### **1. `percona_installer`**
This is the main entry point for the installer. It orchestrates the installation process by calling the relevant modules and functions.

- **Key Functions**:
  - **`main()`**:
    - Entry point for the script.
    - Initializes the installer and displays the menu.
  - **`execute_installation()`**:
    - Handles the installation process by calling appropriate product-specific functions.
  - **`prompt_user()`**:
    - Displays an interactive menu for the user to select a Percona distribution.

---

### **2. `main.py`**
This file contains the core logic for managing user interaction and installation workflows.

- **Key Functions**:
  - **`start_cli_mode()`**:
    - Launches the command-line interface mode.
  - **`start_gui_mode()`**:
    - Launches the GUI mode using the `curses` library.
  - **`install_product(product)`**:
    - Initiates the installation of the selected product.
  - **`validate_platform()`**:
    - Checks the compatibility of the user’s system for the selected product.

---

### **3. `fetch_versions.py`**
Responsible for fetching the latest available versions of Percona distributions.

- **Key Functions**:
  - **`fetch_product_versions(product)`**:
    - Connects to the Percona repository to retrieve the latest versions of the selected product.
  - **`parse_version_data(data)`**:
    - Parses the retrieved data to extract version information.
  - **`get_latest_version(product)`**:
    - Returns the latest version of a specific product.

---

### **4. `supported_platforms.py`**
Handles platform detection and compatibility checks.

- **Key Functions**:
  - **`detect_platform()`**:
    - Identifies the operating system and distribution (e.g., Ubuntu, CentOS).
  - **`is_supported_platform(platform)`**:
    - Verifies if the detected platform supports the selected Percona product.
  - **`get_supported_products(platform)`**:
    - Returns a list of products supported on the current platform.

---

### **5. `gui.py`**
Implements the GUI mode using the `curses` library for a console-based graphical interface.

- **Key Functions**:
  - **`render_menu(options)`**:
    - Displays an interactive menu for the user to select an option.
  - **`handle_input()`**:
    - Captures user input and processes the selected option.
  - **`render_product_details(product)`**:
    - Displays detailed information about the selected product.

---

### **6. `components.json`**
A JSON file containing metadata about supported Percona products.

- **Contents**:
  - Product names.
  - Supported versions.
  - Platform compatibility.

---

## Example Workflow

### Direct Execution
1. Run the script:
   ```bash
   ./percona_installer
   ```

2. Follow the prompts to select and install a Percona distribution.

3. Verify the installation by running:
   ```bash
   percona --version
   ```

### Docker Usage
1. Build the Docker image:
   ```bash
   docker build -t percona_installer_image .
   ```

2. Start the container:
   ```bash
   docker run --rm -it percona_installer_image
   ```

3. Use the installer inside the container.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-branch-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-branch-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the code under the terms of this license.

---
