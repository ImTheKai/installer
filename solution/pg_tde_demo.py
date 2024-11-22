import subprocess

def pg_tde_demo(pkg_manager, output_callback=print):
    """
    Sets up the PostgreSQL database and table with pg_tde settings.

    :param os_type: The operating system type ('deb' for Debian/Ubuntu, 'rpm' for RedHat-based systems).
    :param database: The name of the database to create.
    :param table: The name of the table to create.
    :param output_callback: A function to handle output (default is print).
    """
    
    database = "supersecure"
    table = "albums"

    try:
        # Configure shared_preload_libraries
        output_callback("Setting shared_preload_libraries to 'pg_tde'...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-c", 
             "ALTER SYSTEM SET shared_preload_libraries ='pg_tde';"],
            check=True
        )

        # Enable WAL encryption
        output_callback("Enabling WAL encryption...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-c", 
             "ALTER SYSTEM SET pg_tde.wal_encrypt = on;"],
            check=True
        )

        # Restart PostgreSQL based on OS type
        if pkg_manager == "apt-get":
            output_callback("Restarting PostgreSQL service for Debian/Ubuntu...\n")
            subprocess.run(["sudo", "systemctl", "restart", "postgresql"], check=True)
            key_location = "/var/lib/postgresql/pg_tde_test_keyring.per"
        else:  # Assume 'rpm' for RedHat-based systems
            output_callback("Restarting PostgreSQL service for RedHat-based systems...\n")
            subprocess.run(["sudo", "systemctl", "restart", "postgresql-17"], check=True)
            key_location = "/var/lib/pgsql/pg_tde_test_keyring.per"

        # Create the database
        output_callback(f"Creating database {database}...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-c", 
             f"CREATE DATABASE {database} WITH OWNER=postgres;"],
            check=True
        )

        # Enable pg_tde extension
        output_callback(f"Enabling pg_tde extension in database {database}...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-d", database, "-c", 
             "CREATE EXTENSION pg_tde;"],
            check=True
        )

        # Add key provider file
        output_callback("Adding key provider file for pg_tde...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-d", database, "-c", 
             f"SELECT pg_tde_add_key_provider_file('file-vault', '{key_location}');"],
            check=True
        )

        # Set the principal key
        output_callback("Setting the principal key for pg_tde...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-d", database, "-c", 
             "SELECT pg_tde_set_principal_key('test-db-master-key', 'file-vault');"],
            check=True
        )

        # Set default table access method
        output_callback(f"Setting default_table_access_method to 'tde_heap' for {database}...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-d", database, "-c", 
             f"ALTER DATABASE {database} SET default_table_access_method='tde_heap';"],
            check=True
        )

        # Reload configuration
        output_callback("Reloading PostgreSQL configuration...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-c", 
             "SELECT pg_reload_conf();"],
            check=True
        )

        # Create the table
        output_callback(f"Creating table {table} in database {database}...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-d", database, "-c", 
             f"CREATE TABLE {table} ("
             "album_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
             "artist_id INTEGER, "
             "title TEXT NOT NULL, "
             "released DATE NOT NULL);"],
            check=True
        )

        # Verify encryption
        output_callback(f"Verifying encryption status for table {table}...\n")
        subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-U", "postgres", "-d", database, "-c", 
             f"SELECT pg_tde_is_encrypted('{table}');"],
            check=True
        )

        output_callback("Database and table setup completed successfully.\n")
    except subprocess.CalledProcessError as e:
        output_callback(f"Error during database and table creation: {str(e)}\n")
    except Exception as e:
        output_callback(f"Unexpected error: {str(e)}\n")
