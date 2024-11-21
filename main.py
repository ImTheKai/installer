import sys
from cli import run_cli
from gui import run_gui

def parse_arguments(args=None):
    """
    Parse command-line arguments if provided. Return a dictionary of arguments.
    """
    if args is None:
        args = sys.argv[1:]  # Default to sys.argv if no arguments provided

    # Check if argparse is available
    try:
        import argparse
        parser = argparse.ArgumentParser(description="Percona Installer Argument Parser")

        # Add arguments to the parser
        parser.add_argument('-r', '--repository', type=str, help="main/testing/experimental")
        parser.add_argument('-p', '--product', type=str, help="ppg-17.0/ps-80/pxc-80/psmdb-80")
        parser.add_argument('-c', '--components', type=str, help="percona-postgresql-17 pg_tde/percona-server-mongodb")
        parser.add_argument('--verbose', action='store_true', help="Enable verbose output")

        # Parse arguments
        parsed_args = parser.parse_args(args)
        return vars(parsed_args)  # Convert Namespace to a dictionary for easy use
    except ImportError:
        print("`argparse` module is not available. Running interactively...")
        return None


def main():
    """
    Main entry point for the installer. Detects mode and executes the appropriate workflow.
    """
    args = parse_arguments()

    if args:  # If arguments are parsed, assume CLI mode
        run_cli(args)
    else:  # No arguments or argparse unavailable, use interactive mode
        print("Welcome to the Percona Installer!")
        print("1. CLI Mode")
        print("2. GUI Mode (Console)")
        choice = input("Select a mode (1 or 2): ").strip()

        if choice == "1":
            print("Entering CLI Mode.")
            repo = input("Enter repository (main/testing/experimental): ").strip()
            product = input("Enter product (ppg-17.0/ps-80/pxc-80/psmdb-80): ").strip()
            components = input("Enter components (comma-separated): ").strip()
            verbose = input("Enable verbose output? (y/n): ").strip().lower() == 'y'

            # Create a dictionary to mimic parsed arguments
            cli_args = {
                "repository": repo,
                "product": product,
                "components": components.split(",") if components else None,
                "verbose": verbose
            }
            run_cli(cli_args)
        elif choice == "2":
            print("Entering GUI Mode.")
            run_gui()
        else:
            print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
