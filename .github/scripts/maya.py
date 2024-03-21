import argparse
import hashlib
import glob
import contextlib
import logging
import os
import pathlib
import platform
import re
import requests
import shutil
import sidefx
import subprocess
import tarfile
import zipfile
from urllib import request
import ssl
import json

MAYA_USD_SDK_URL = "https://api.github.com/repos/Autodesk/maya-usd"
MAYA_USD_SDK_RELEASE_ASSET_ELEMENTS_REGEX = re.compile(
    "MayaUSD_([0-9.]+)_Maya([0-9.]+)_(Linux|Windows).(run|exe)"
)
MAYA_PYTHON_VERSION_MAPPING = {
    "2024.2": "3.10.11"
}
PYTHON_SOURCE_DOWNLOAD_URL = {
    "3.10.11": "https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tgz"
}
PYTHON_WINDOWS_DOWNLOAD_URL = {
    "3.10.11": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
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


def get_autodesk_platform():
    """Get the active platform usable for SideFX platform API calls
    Returns:
        str: The active platform
    """
    current_platform = platform.system()
    if current_platform == "Windows" or current_platform.startswith("CYGWIN"):
        return "Windows"
    elif current_platform == "Darwin":
        return "MacOS"
    elif current_platform == "Linux":
        return "Linux"
    else:
        return ""


def get_autodesk_maya_usd_sdk_releases(platform_name, maya_version):
    """Get the GitHub API service
    Args:
        client_id (str): The client id
        client_secret_key (str): The client secret key
    Returns:
        sidefx.Service: The service
    """
    # Query release data
    try:
        with contextlib.closing(
            request.urlopen(
                request.Request(MAYA_USD_SDK_URL + "/releases"),
                context=ssl._create_unverified_context(),
            )
        ) as response:
            data = json.loads(response.read())
    except Exception:
        data = []

    # Extract relevant data
    releases = []
    for release in data:
        # Skip pre releases
        if release["prerelease"]:
            continue
        for asset in release["assets"]:
            if asset["content_type"] not in ("application/x-msdownload", "application/octet-stream"):
                continue
            asset_name = asset["name"]
            asset_name_elements = MAYA_USD_SDK_RELEASE_ASSET_ELEMENTS_REGEX.match(asset_name)
            if not asset_name_elements:
                continue
            (
                asset_usd_sdk_version,
                asset_maya_version,
                asset_platform,
                asset_ext
            ) = asset_name_elements.groups()
            if asset_platform != platform_name:
                continue
            elif asset_maya_version != maya_version:
                continue
            releases.append((asset_usd_sdk_version, asset["browser_download_url"]))

    return releases


def install_autodesk_product(product, version, install_dir_path):
    """Install a USD SDK release of Maya
    Args:
        product (str): The target product name (e.g. maya, etc.)
        version (str|None): The target product version (e.g. 2024.4, etc.)
        install_dir_path (str): The install dir path.
    """
    autodesk_maya_version = version
    python_version = MAYA_PYTHON_VERSION_MAPPING[version]

    # Directories
    download_dir_path = os.path.join(install_dir_path, "download")
    install_dir_path = os.path.join(install_dir_path, "install")
    tmp_dir_path = os.path.join(install_dir_path, "tmp")
    if os.path.exists(download_dir_path):
        shutil.rmtree(download_dir_path)
    if os.path.exists(install_dir_path):
        shutil.rmtree(install_dir_path)
    if os.path.exists(tmp_dir_path):
        shutil.rmtree(tmp_dir_path)
    os.makedirs(download_dir_path)
    os.makedirs(install_dir_path)
    os.makedirs(tmp_dir_path)

    sevenZip_dir_name = "7zip"
    sevenZip_download_dir_path = os.path.join(download_dir_path, sevenZip_dir_name)
    sevenZip_install_dir_path = os.path.join(install_dir_path, sevenZip_dir_name)

    python_dir_name = "python"
    python_download_dir_path = os.path.join(download_dir_path, python_dir_name)
    python_extract_dir_path = os.path.join(tmp_dir_path, python_dir_name)
    python_install_dir_path = os.path.join(install_dir_path, python_dir_name)

    maya_usd_sdk_dir_name = "maya_usd_sdk"
    maya_usd_sdk_download_dir_path = os.path.join(download_dir_path, maya_usd_sdk_dir_name)
    maya_usd_sdk_extract_dir_path = os.path.join(tmp_dir_path, maya_usd_sdk_dir_name)
    maya_usd_sdk_install_dir_path = os.path.join(install_dir_path, maya_usd_sdk_dir_name)

    maya_usd_sdk_devkit_dir_name = "maya_usd_sdk_devkit"
    maya_usd_sdk_devkit_install_dir_path = os.path.join(install_dir_path, maya_usd_sdk_devkit_dir_name)

    config_file_path = os.path.join(install_dir_path, "config.json")

    autodesk_platform = get_autodesk_platform()
    if autodesk_platform == "Linux":
        # Python
        python_download_url = PYTHON_SOURCE_DOWNLOAD_URL[python_version]
        python_download_file_path = os.path.join(python_download_dir_path, "python.tgz")
        logging.info("Downloading Python Build {}".format(python_version))
        download_file(python_download_file_path, python_download_url)
        with tarfile.open(python_download_file_path, "r") as python_download_file:
            python_download_file.extractall(python_extract_dir_path, filter='data')
        python_version_dir_path = os.path.join(python_extract_dir_path, os.listdir(python_extract_dir_path)[0])
        python_configure_file_path = os.path.join(python_version_dir_path, "configure")
        os.chmod(python_configure_file_path, 0o777)
        logging.info("Configuring Python Build")
        command = [python_configure_file_path, "--enable-shared", "--prefix", python_install_dir_path]
        process = subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=python_version_dir_path)
        logging.info("Building Python")
        process = subprocess.check_call(["make"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=python_version_dir_path)
        logging.info("Installing Python")
        process = subprocess.check_call(["make", "install"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=python_version_dir_path)
        # Maya USD SDK
        maya_usd_sdk_releases = get_autodesk_maya_usd_sdk_releases(autodesk_platform, autodesk_maya_version)
        maya_usd_sdk_latest_release = maya_usd_sdk_releases[0]
        maya_usd_sdk_version = maya_usd_sdk_latest_release[0]
        maya_usd_sdk_download_url = maya_usd_sdk_latest_release[1]
        maya_usd_sdk_download_file_path = os.path.join(maya_usd_sdk_download_dir_path, "maya_usd_sdk.run")
        logging.info("Downloading Maya USD SDK (Release {})".format(maya_usd_sdk_version))
        download_file(maya_usd_sdk_download_file_path, maya_usd_sdk_download_url)
        logging.info("Installing Maya USD SDK")
        os.chmod(maya_usd_sdk_download_file_path, 777)
        os.makedirs(maya_usd_sdk_extract_dir_path)
        command = [maya_usd_sdk_download_file_path, "--tar", "xvf", "--directory", maya_usd_sdk_extract_dir_path]
        process = subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        maya_usd_sdk_extract_rpm_file_name = [f for f in os.listdir(maya_usd_sdk_extract_dir_path) if f.endswith(".rpm")][0]
        maya_usd_sdk_extract_rpm_file_path = os.path.join(maya_usd_sdk_extract_dir_path, maya_usd_sdk_extract_rpm_file_name)
        # command = ["rpm", "-e", maya_usd_sdk_extract_rpm_file_name.replace(".rpm", "")]
        # process = subprocess.check_call(command, cwd=maya_usd_sdk_extract_dir_path)
        command = ["rpm", "-i", "--nodeps","--prefix", maya_usd_sdk_extract_dir_path, maya_usd_sdk_extract_rpm_file_path]
        process = subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=maya_usd_sdk_extract_dir_path)
        maya_usd_sdk_extract_usd_dir_path = glob.glob("{root_dir}{sep}**{sep}mayausd{sep}USD".format(root_dir=maya_usd_sdk_extract_dir_path, sep=os.path.sep), recursive=True)[0]
        maya_usd_sdk_extract_usd_dir_path = os.path.join(maya_usd_sdk_extract_dir_path, maya_usd_sdk_extract_usd_dir_path)
        os.rename(maya_usd_sdk_extract_usd_dir_path, maya_usd_sdk_install_dir_path)
        os.chmod(maya_usd_sdk_install_dir_path, 0o777)
        # Maya USD SDK devkit
        maya_usd_sdk_devkit_zip_file_path = glob.glob("{root_dir}{sep}**{sep}devkit.zip".format(root_dir=maya_usd_sdk_install_dir_path, sep=os.path.sep), recursive=True)
        maya_usd_sdk_devkit_zip_file_path = os.path.join(maya_usd_sdk_install_dir_path, maya_usd_sdk_devkit_zip_file_path[0])
        with zipfile.ZipFile(maya_usd_sdk_devkit_zip_file_path, 'r') as zip_file:
            zip_file.extractall(maya_usd_sdk_devkit_install_dir_path)

    elif autodesk_platform == "Windows":
        # Python
        python_download_url = PYTHON_WINDOWS_DOWNLOAD_URL[python_version]
        python_download_file_path = os.path.join(python_download_dir_path, "python.exe")
        logging.info("Downloading Python Build {}".format(python_version))
        download_file(python_download_file_path, python_download_url)
        logging.info("Installing Python")
        command = [python_download_file_path, "/passive", "/quiet", "InstallAllUsers=0",
                   "TargetDir={}".format(python_install_dir_path), "AssociateFiles=0",
                   "Shortcuts=0", "Include_doc=0", "Include_launcher=0", "Include_test=0"]
        process = subprocess.check_call(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        # Maya USD SDK
        maya_usd_sdk_releases = get_autodesk_maya_usd_sdk_releases(autodesk_platform, autodesk_maya_version)
        maya_usd_sdk_latest_release = maya_usd_sdk_releases[0]
        maya_usd_sdk_version = maya_usd_sdk_latest_release[0]
        maya_usd_sdk_download_url = maya_usd_sdk_latest_release[1]
        maya_usd_sdk_download_file_path = os.path.join(maya_usd_sdk_download_dir_path, "maya_usd_sdk.exe")
        logging.info("Downloading Maya USD SDK (Release {})".format(maya_usd_sdk_version))
        download_file(maya_usd_sdk_download_file_path, maya_usd_sdk_download_url)
        command = [serverZip_exe_file_path, "x", maya_usd_sdk_download_file_path, "-o{}".format(maya_usd_sdk_extract_dir_path)]
        process = subprocess.check_call(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("Installing Maya USD SDK")
        command = ["msiexec", "/i", os.path.join(maya_usd_sdk_extract_dir_path, "MayaUSD.msi"), "/quiet", "/passive", "INSTALLDIR={}".format(maya_usd_sdk_extract_dir_path)]
        process = subprocess.check_call(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        maya_usd_sdk_extract_usd_dir_path = glob.glob("{root_dir}{sep}**{sep}mayausd{sep}USD".format(root_dir=maya_usd_sdk_extract_dir_path, sep=os.path.sep), recursive=True)[0]
        maya_usd_sdk_extract_usd_dir_path = os.path.join(maya_usd_sdk_extract_dir_path, maya_usd_sdk_extract_usd_dir_path)
        os.rename(maya_usd_sdk_extract_usd_dir_path, maya_usd_sdk_install_dir_path)
        # Maya USD DevKit
        logging.info("Installing Maya USD SDK DevKit")
        maya_usd_sdk_devkit_zip_file_path = glob.glob("{root_dir}{sep}**{sep}devkit.zip".format(root_dir=maya_usd_sdk_install_dir_path, sep=os.path.sep), recursive=True)
        maya_usd_sdk_devkit_zip_file_path = os.path.join(maya_usd_sdk_install_dir_path, maya_usd_sdk_devkit_zip_file_path[0])
        with zipfile.ZipFile(maya_usd_sdk_devkit_zip_file_path, 'r') as zip_file:
            zip_file.extractall(maya_usd_sdk_devkit_install_dir_path)

    # Store configuration
    with open(config_file_path, "w") as config_file:
        config = {
            "python": python_version,
            "maya": autodesk_maya_version,
            "maya_usd_sdk": maya_usd_sdk_version,
        }
        json.dump(config, config_file)


def create_autodesk_maya_artifact(artifact_src, artifact_dst, artifact_prefix, artifact_product_name, dependency_dir_path):
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
    with open(config_file_path, "w") as config_file:
        config = json.load(config_file)

    maya_version = config["maya"]
    maya_usd_sdk_version = config["maya_usd_sdk"]
    autodesk_platform = get_autodesk_platform()
    artifact_file_path = os.path.join(
        artifact_dst, f"{artifact_prefix}_{artifact_product_name}-{maya_version}-USD-SDK-{maya_usd_sdk_version}-{autodesk_platform}"
    )
    artifact_dir_path = os.path.dirname(artifact_file_path)
    if not os.path.exists(artifact_dir_path):
        os.makedirs(artifact_dir_path)
    shutil.make_archive(artifact_file_path, "zip", artifact_src)


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install Maya USD SDK")
    parser.add_argument(
        "--install_maya_product_name",
        help="Maya product name to install. If not provided, fallback to the default.",
    )
    parser.add_argument(
        "--install_maya_product_version",
        help="Maya product version to install. If not provided, fallback to the latest version.",
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
    # Install Maya USD SDK
    if args.install:
        install_autodesk_product(args.install_maya_product_name,
                                 args.install_maya_product_version,
                                 args.install_directory)
    # Create artifact tagged with Maya build name (expects Maya USD SDK to be installed via the above install command)
    if args.artifact:
        create_autodesk_maya_artifact(
            args.artifact_src, args.artifact_dst, args.artifact_prefix, args.artifact_product_name, args.artifact_product_version, args.install_directory
        )