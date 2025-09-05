import argparse
import logging
import os
import platform
import requests
import shutil
import subprocess
import json


USD_COMPILED_DOWNLOAD_URL = {
    "25.05": {
        "Windows": "https://developer.nvidia.com/downloads/USD/usd_binaries/25.05/usd.py311.windows-x86_64.usdview.release-0.25.05-25f3d3d8.zip",
        "Linux": "https://developer.nvidia.com/downloads/USD/usd_binaries/25.05/usd.py311.manylinux_2_35_x86_64.usdview.release@0.25.05-25f3d3d8.zip"
    },
    "24.11": {
        "Windows": "https://developer.nvidia.com/downloads/USD/usd_binaries/24.11/usd.py311.windows-x86_64.usdview.release-0.24.11-4d81dd85.zip",
        "Linux": "https://developer.nvidia.com/downloads/USD/usd_binaries/24.11/usd.py311.manylinux_2_35_x86_64.usdview.release-0.24.11-4d81dd85.zip"
    }
}
SEVENZIP_WINDOWS_DOWNLOAD_URL = {
    "2301": "https://www.7-zip.org/a/7z2401-x64.exe"
}


logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.INFO)


def download_file(download_file_path, download_url):
    """Download the release to the directory
    Args:
        download_file_path (str): The target file
        download_url (str): The download url
    Returns:
        str: The file path of the downloaded file
    """
    # Download file
    download_dir_path = os.path.dirname(download_file_path)
    if not os.path.exists(download_dir_path):
        os.makedirs(download_dir_path)
    request = requests.get(download_url, stream=True)
    if request.status_code == 200:
        with open(download_file_path, "wb") as download_file:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, download_file)
    else:
        raise Exception("Error downloading file | {}".format(download_url))
    return download_file_path


def get_standalone_platform():
    """Get the active platform usable for SideFX platform API calls
    Returns:
        str: The active platform
    """
    current_platform = platform.system()
    if current_platform == "Windows" or current_platform.startswith("CYGWIN"):
        return "Windows"
    elif current_platform == "Linux":
        return "Linux"
    raise Exception(f"Platform not supported: {current_platform}")


def install_standalone_product(product, version, dependency_dir_path):
    """Install a standalone USD release
    Args:
        version (str|None): The target product version (e.g. 2024.4, etc.)
        dependency_dir_path (str): The install dir path.
    """

    # Directories
    download_dir_path = os.path.join(dependency_dir_path, "download")
    install_dir_path = os.path.join(dependency_dir_path, "install")
    if os.path.exists(download_dir_path):
       shutil.rmtree(download_dir_path)
    if os.path.exists(install_dir_path):
       shutil.rmtree(install_dir_path)
    os.makedirs(download_dir_path)
    os.makedirs(install_dir_path)

    sevenZip_dir_name = "7zip"
    sevenZip_download_dir_path = os.path.join(download_dir_path, sevenZip_dir_name)
    sevenZip_install_dir_path = os.path.join(install_dir_path, sevenZip_dir_name)

    usd_standalone_dir_name = "usd_standalone"
    usd_standalone_download_dir_path = os.path.join(download_dir_path, usd_standalone_dir_name)
    usd_standalone_install_dir_path = os.path.join(install_dir_path, usd_standalone_dir_name)

    config_file_path = os.path.join(install_dir_path, "config.json")

    standalone_platform = get_standalone_platform()

    # USD
    usd_standalone_download_url = USD_COMPILED_DOWNLOAD_URL[version][standalone_platform]
    usd_standalone_download_file_path = os.path.join(usd_standalone_download_dir_path, "usd_standalone.zip")
    logging.info("Downloading USD Build {}".format(version))
    download_file(usd_standalone_download_file_path, usd_standalone_download_url)
    logging.info("Extracting USD Build")
    if standalone_platform == "Windows":
        # 7Zip
        serverZip_version = "2301"
        serverZip_download_url = SEVENZIP_WINDOWS_DOWNLOAD_URL[serverZip_version]
        serverZip_download_file_path = os.path.join(sevenZip_download_dir_path, "7zip.exe")
        logging.info("Downloading 7zip (Build {})".format(serverZip_version))
        download_file(serverZip_download_file_path, serverZip_download_url)
        logging.info("Installing 7zip")
        command = [serverZip_download_file_path, "/S", "/D={}".format(sevenZip_install_dir_path)]
        process = subprocess.check_call(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        serverZip_exe_file_path = os.path.join(sevenZip_install_dir_path, "7z.exe")
        # Unzip
        command = [serverZip_exe_file_path, "x", usd_standalone_download_file_path, "-o{}".format(usd_standalone_install_dir_path)]
        process = subprocess.check_call(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif standalone_platform == "Linux":
        # Unzip
        command = ["7z", "x", f"-o{usd_standalone_install_dir_path}", usd_standalone_download_file_path]
        process = subprocess.check_call(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Store configuration
    python_version = os.path.basename(usd_standalone_download_url).split(".")[1]
    with open(config_file_path, "w") as config_file:
        config = {
            "python": python_version,
            "usd": version,
        }
        json.dump(config, config_file)


def create_standalone_artifact(artifact_src, artifact_dst, artifact_prefix, artifact_product_name, dependency_dir_path):
    """Create a .zip artifact based on the source directory content.
    The output name will have will end in the houdini build name.

    Args:
        artifact_src (str): The source directory
        artifact_dst (str): The target directory
        artifact_prefix (str): The file name prefix, the suffix will be the Houdini build name
        artifact_product_name (str): The file name product name. 
                                     This defines the Maya product name, e.g. like 'maya'
        dependency_dir_path (str): The dependency install directory path.
    Returns:
        str: The artifact file path
    """
    install_dir_path = os.path.join(dependency_dir_path, "install")
    config_file_path = os.path.join(install_dir_path, "config.json")
    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)

    usd_version = config["usd"]
    python_version = config["python"]
    standalone_platform = get_standalone_platform()
    artifact_file_path = os.path.join(
        artifact_dst, f"{artifact_prefix}_{artifact_product_name}-{usd_version}-{python_version}-{standalone_platform}"
    )
    artifact_dir_path = os.path.dirname(artifact_file_path)
    if not os.path.exists(artifact_dir_path):
        os.makedirs(artifact_dir_path)
    shutil.make_archive(artifact_file_path, "zip", artifact_src)


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install the standalone pre-compiled USD build")
    parser.add_argument(
        "--install_standalone_product_name",
        help="Standalone product name to install. If not provided, fallback to the default.",
    )
    parser.add_argument(
        "--install_standalone_product_version",
        help="USD product version to install.",
    )
    parser.add_argument(
        "--install_directory",
        help="The installation directory.",
    )
    parser.add_argument("--artifact", action="store_true", help="Create artifact")
    parser.add_argument("--artifact_src", help="Artifact source directory")
    parser.add_argument("--artifact_dst", help="Artifact target directory")
    parser.add_argument("--artifact_prefix", help="Artifact name prefix")
    parser.add_argument("--artifact_product_name", help="Artifact product name")
    args = parser.parse_args()
    # Execute
    # Install precompiled standalone USD with headers
    if args.install:
        install_standalone_product(
            args.install_standalone_product_name,
            args.install_standalone_product_version,
            args.install_directory
        )
    # Create artifact tagged with stand build name (expects standalone USD build to be installed via the above install command)
    if args.artifact:
        create_standalone_artifact(
            args.artifact_src, args.artifact_dst, args.artifact_prefix, args.artifact_product_name, args.install_directory
        )