
from cli import run_cli
from gui import run_gui

if __name__ == "__main__":
    print("Welcome to the Percona Installer!")
    print("1. CLI Mode")
    print("2. GUI Mode (Console)")
    choice = input("Select a mode (1 or 2): ").strip()

    if choice == "1":
        run_cli()
    elif choice == "2":
        run_gui()
    else:
        print("Invalid choice. Exiting.")
