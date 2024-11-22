# Percona Installer

The **Percona Installer** is a Python-based utility designed to simplify the installation and configuration of Percona software distributions. It provides an intuitive CLI and GUI interface to set up repositories, install components, and configure Percona products on supported platforms.

---

## Features

- **Supports multiple Percona distributions**:
  - Percona Server for MySQL
  - Percona XtraDB Cluster (PXC)
  - Percona Distribution for MongoDB
  - Percona Distribution for PostgreSQL
- **Interactive installation process**:
  - Step-by-step guidance through CLI or GUI interfaces.
- **Command-line automation**:
  - Supports argument-driven installation for scripting.
- **Platform detection**:
  - Automatically identifies the operating system and selects the appropriate package manager.
- **Extensible design**:
  - Modular architecture for adding new features or customizing behavior.
- **Docker support**:
  - Run the installer in a containerized environment.

---

## Prerequisites

- Python 3.6 or higher
- Required Python libraries (see `requirements.txt`)
- `curses` library (required for GUI mode)
- `sudo` or root access for installing Percona packages
- Internet connectivity for downloading dependencies and packages

---

## Installation

### Clone the Repository

1. Clone the repository:
   ```bash
   sudo git clone https://github.com/EvgeniyPatlan/installer.git /opt/installer
   cd /opt/installer/
   ```

2. Install required dependencies:
   ```bash
   sudo python3 -m pip install -r requirements.txt --break-system-packages
   ```

3. Add the `percona_installer` script to `/usr/bin` for global access:
   ```bash
   sudo cp percona_installer /usr/bin/
   sudo chmod +x /usr/bin/percona_installer
   ```

### Docker Installation

1. Build the Docker image:
   ```bash
   docker build -t percona_installer_image .
   ```

2. Run the installer inside a container:
   ```bash
   docker run --rm -it percona_installer_image
   ```

---

## Usage

### CLI Mode

Run the installer with command-line arguments for fully automated installation:

```bash
percona_installer -r <repository> -p <product> -c <components> [--verbose]
```

- **Arguments**:
  - `-r, --repository`: Specify the repository type (`main`, `testing`, `experimental`).
  - `-p, --product`: Specify the product and version (e.g., `ppg-17.0`, `ps-80`).
  - `-c, --components`: List of components to install (comma-separated).
  - `-s, --solution`: Specify the solution you want to use [optional] (e.g., `pg_tde_demo`).
  - `--verbose`: Enable verbose output for debugging.

#### Examples:

1. Install Percona PostgreSQL 17.0:
   ```bash
   percona_installer -r release -p ppg-17.0 -c percona-postgresql-17
   ```

2. Install the nightly build of Percona PostgreSQL 17.0 and pg_tde and run the solution script pg_tde_demo:
   ```bash
   sudo percona_installer -r experimental -p ppg-17.0 -c percona-postgresql-17,percona-postgresql-17-pg-tde -s pg_tde_demo
   ```

3. Install Percona XtraDB Cluster 8.0:
   ```bash
   percona_installer main.py -r testing -p pxc-80 -c percona-xtradb-cluster-8.0 --verbose
   ```

##### **`NOTE`**

If you want to learn more about existing solutions, look into the `solutions/` folder and read the description at the top of each file.   

---

## Components Configuration

The `components.json` file defines the available components for each product. You can customize it to add, modify, or remove components.

### Example `components.json`:
```json
{
  "Percona Server for MySQL": {
    "components": [
      "percona-server-client",
      "percona-server-server",
      "percona-toolkit"
    ]
  },
  "Percona Distribution for PostgreSQL": {
    "components": [
      "percona-postgresql",
      "pg_stat_monitor"
    ]
  }
}
```

---

## Adding Your Own Solutions

The project now supports a highly modular approach to defining solutions. You can easily create your own custom solutions by following these steps:

1. **Create a Python Script**:
   - Navigate to the `solutions/` folder.
   - Create a new Python file named after your desired solution. For example, if your solution is `my_solution`, the file should be named `my_solution.py`.

2. **Define the Main Function**:
   - The main function inside the file **must have the same name as the file**. For example:
     ```python
     # solutions/my_solution.py
     def my_solution():
         print("Hello from my_solution!")
     ```

3. **Automatic Detection**:
   - The cli.py script dynamically imports all Python scripts under the solutions/ folder and makes them available for execution via the command line interface (CLI).
     The function will automatically be loaded and callable by name.

---

## Code Architecture

### **1. `main.py`**
Handles the main execution flow, including CLI and GUI mode initialization.

- **Functions**:
  - `parse_arguments`: Parses command-line arguments.
  - `main`: Entry point for the installer.

### **2. `cli.py`**
Implements the command-line interface logic.

- **Functions**:
  - `run_cli`: Handles both argument-driven and interactive CLI modes.
  - `enable_repository`: Enables the selected repository.
  - `install_components`: Installs selected components.

### **3. `gui.py`**
Implements the GUI mode using `npyscreen`.

- **Classes**:
  - `InstallerApp`: Manages GUI forms and workflows.
  - `MainForm`: Handles distribution and version selection.
  - `RepoSetupForm`: Enables repositories for selected distributions.
  - `ComponentSelectionForm`: Manages component selection and installation.

### **4. `fetch_versions.py`**
Fetches available versions for Percona products from the repository.

- **Functions**:
  - `fetch_all_versions`: Retrieves versions matching a product prefix.
  - `download_repo_index`: Downloads the repository index page.

### **5. `shared.py`**
Contains shared utilities, constants, and helper functions.

- **Functions**:
  - `detect_os`: Identifies the operating system and package manager.
  - `ensure_percona_release`: Installs the `percona-release` package.
  - `build_repo_command`: Constructs commands for enabling repositories.

---

## Troubleshooting

### Common Issues

1. **Missing `sudo`**:
   - Ensure `sudo` is installed and in the system PATH.
   - Use root privileges if `sudo` is unavailable.

2. **`curses` Library Errors**:
   - Install the `curses` library for your Python version.

3. **Network Errors**:
   - Verify internet connectivity.
   - Check firewall or proxy settings.

4. **Unsupported Distribution**:
   - Ensure your Linux distribution is supported.

---

## Contribution

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
