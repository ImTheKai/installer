from shared import logger

import re
import requests
from bs4 import BeautifulSoup
import logging

INDEX_URL = "https://repo.percona.com/"
INDEX_FILE = "index.html"

def download_repo_index():
    """Download and save the index page of repo.percona.com."""
    try:
        logger.info(f"Downloading {INDEX_URL}...")
        response = requests.get(INDEX_URL, timeout=10)
        response.raise_for_status()

        with open(INDEX_FILE, "w", encoding="utf-8") as file:
            file.write(response.text)

        logger.info(f"Successfully downloaded {INDEX_URL}.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {INDEX_URL}: {str(e)}")
        raise Exception(f"Error downloading {INDEX_URL}: {str(e)}")

def extract_version(directory, prefix):
    """
    Extract the version number from a directory name.

    Example:
    For `pdpxc-8.0.26`, it extracts `8.0.26` if the prefix is `pdpxc-`.
    """
    pattern = rf"{re.escape(prefix)}([\d.]+)"  # Match versions after the prefix
    match = re.search(pattern, directory)
    return match.group(1) if match else None

def fetch_all_versions(prefix):
    """Fetch all versions for a Percona distribution."""
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        logger.info(f"{INDEX_FILE} not found. Downloading it now...")
        download_repo_index()
        with open(INDEX_FILE, "r", encoding="utf-8") as file:
            html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    links = [link.text.strip("/") for link in soup.find_all("a", href=True)]

    # Filter directories matching the prefix
    relevant_dirs = [link for link in links if link.startswith(prefix)]
    logger.info(f"Found directories for prefix '{prefix}': {relevant_dirs}")

    # Extract versions and group by major version
    versions = []
    for directory in relevant_dirs:
        version = extract_version(directory, prefix)
        if version:
            versions.append(version)

    # Sort all versions numerically
    sorted_versions = sorted(
        versions,
        key=lambda v: [int(part) if part.isdigit() else 0 for part in v.split(".")],
        reverse=True,
    )
    logger.info(f"Fetched versions for prefix '{prefix}': {sorted_versions}")
    return sorted_versions

