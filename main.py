import sys
from cli import run_cli
from gui import run_gui

def parse_arguments(args=None):
    """
    Parse command-line arguments if provided. Return a dictionary of arguments.
    """
    if args is None:
        args = sys.argv[1:]

    try:
        import argparse
        parser = argparse.ArgumentParser(description="Percona Installer Argument Parser")
        parser.add_argument('-r', '--repository', type=str, help="main/testing/experimental")
        parser.add_argument('-p', '--product', type=str, help="ppg-17.0/ps-80/pxc-80/psmdb-80")
        parser.add_argument('-c', '--components', type=str, help="Comma-separated list of components")
        parser.add_argument('--verbose', action='store_true', help="Enable verbose output")
        parsed_args = parser.parse_args(args)
        return vars(parsed_args)
    except ImportError:
        print("`argparse` module is not available. Running interactively...")
        return None

def main():
    """
    Main entry point for the installer.
    """
    args = parse_arguments()

    # If arguments are parsed but empty or invalid, fallback to interactive mode
    if args and any(args.values()):
        try:
            run_cli(args)
        except Exception as e:
            print(f"Error in CLI mode: {e}")
            sys.exit(1)
    else:
        # No arguments or invalid arguments: fallback to interactive mode
        print("Welcome to the Percona Installer!")
        print("1. CLI Mode")
        print("2. GUI Mode (Console)")
        choice = input("Select a mode (1 or 2): ").strip()

        if choice == "1":
            run_cli()  # Interactive CLI mode
        elif choice == "2":
            run_gui()
        else:
            print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()

