
# Percona Installer

This installer allows you to install Percona software distributions with ease. It supports both CLI and console-based GUI modes.

## Usage

0. Clone or download this repository into /opt/.
1. ```bash
   pip3 install -r requirements.txt
   ```
2. copy percona_installer into /usr/bin
3. execute percona_installer
4. Choose between CLI and GUI modes.

### Requirements
- Python 3.6+
- `curses` (for GUI mode)
- `percona-release`

### Supported Distributions
- Percona Server for MySQL
- Percona Distribution for MySQL (PXC)
- Percona Distribution for MongoDB
- Percona Distribution for PostgreSQL
