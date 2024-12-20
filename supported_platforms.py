from shared import SUPPORTED_PLATFORMS, NORMALIZED_DISTROS

import platform

def normalize_distro_name(distro_name):
    """Normalize distro name to match supported platforms."""
    return NORMALIZED_DISTROS.get(distro_name.lower(), distro_name)

def check_major_version(version):
    """Extract major version (e.g., '8' from '8.10')."""
    return version.split('.')[0]

def check_platform():
    """Check if the current platform is supported."""
    system = platform.system()
    if system != "Linux":
        return False, "This installer is supported only on Linux systems."

    try:
        # Try legacy method
        distro, version, _ = platform.linux_distribution()
    except AttributeError:
        # Use 'distro' package for modern systems
        import distro
        distro, version = distro.id(), distro.version()

    distro = normalize_distro_name(distro.strip())
    major_version = check_major_version(version.strip())

    for supported_distro, versions in SUPPORTED_PLATFORMS.items():
        if supported_distro == distro and major_version in versions:
            return True, (distro, version)

    return False, f"Unsupported platform: {distro} {version}. Supported platforms: {SUPPORTED_PLATFORMS}"

