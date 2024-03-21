import argparse
import hashlib
import glob
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


SIDEFX_CLIENT_ID = os.environ.get("SIDEFX_CLIENT_ID", "")
SIDEFX_CLIENT_SECRET_KEY = os.environ.get("SIDEFX_CLIENT_SECRET_KEY", "")


logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")


def create_github_service(client_id, client_secret_key):
    """Get the GitHub API service
    Args:
        client_id (str): The client id
        client_secret_key (str): The client secret key
    Returns:
        sidefx.Service: The service
    """
    return sidefx.service(
        access_token_url="https://www.sidefx.com/oauth2/application_token",
        client_id=client_id,
        client_secret_key=client_secret_key,
        endpoint_url="https://www.sidefx.com/api/",
    )


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


def download_sidefx_product_release(dir_path, release):
    """Download the release to the directory
    Args:
        dir_path (str): The target directory
        release (dict): The download build release dict
    Returns:
        str: The file path of the downloaded file
    """
    # Download file
    download_file_name = release["filename"]
    download_file_path = os.path.join(dir_path, download_file_name)
    request = requests.get(release["download_url"], stream=True)
    if request.status_code == 200:
        with open(download_file_path, "wb") as download_file:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, download_file)
    else:
        raise Exception("Error downloading file!")
    # Verify file checksum
    # 10.12.23 -> SideFX Bug, this currently fails on Linux
    # download_file_hash = hashlib.md5()
    # with open(download_file_path, "rb") as download_file:
    #     for chunk in iter(lambda: download_file.read(4096), b""):
    #         download_file_hash.update(chunk)
    # if download_file_hash.hexdigest() != release["hash"]:
    #     raise Exception("Checksum does not match!")
    return download_file_path


def install_autodesk_product(product, version):
    """Install the latest production release of Houdini
    Args:
        product (str): The target product name (e.g. houdini, houdini-py39, etc.)
        version (str|None): The target product version (e.g. 20.0, 19.5, etc.)
    """
    # Connect to SideFX API
    logging.info("Connecting to SideFX API")
    sidefx_service = create_sidefx_service(SIDEFX_CLIENT_ID, SIDEFX_CLIENT_SECRET_KEY)
    sidefx_platform = get_sidefx_platform()
    sidefx_product_name = product
    sidefx_product_version = version

    # Get release data
    releases_list = sidefx_service.download.get_daily_builds_list(
        product=sidefx_product_name,
        version=sidefx_product_version,
        platform=sidefx_platform,
        only_production=True,
    )
    target_release = None
    if sidefx_platform == "linux":
        for release in releases_list:
            # Switch to new gcc version starting with H20
            if release["version"] == "20.0":
                if not release["platform"].endswith("gcc11.2"):
                    continue
            target_release = release
            break
    else:
        for release in releases_list:
            target_release = release
            break

    if not target_release:
        raise Exception(
            "No Houdini version found for requested version | {}".format(
                houdini_version
            )
        )

    target_release_download = sidefx_service.download.get_daily_build_download(
        product="houdini",
        version=target_release["version"],
        build=target_release["build"],
        platform=sidefx_platform,
    )

    # Download latest production release
    logging.info(
        "Downloading Houdini build {version}.{build}".format(
            version=target_release["version"], build=target_release["build"]
        )
    )
    downloads_dir_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isdir(downloads_dir_path):
        os.makedirs(downloads_dir_path)
    houdini_installer_file_path = download_sidefx_product_release(
        downloads_dir_path, target_release_download
    )
    # Install latest production release
    logging.info(
        "Installing Houdini build {version}.{build}".format(
            version=target_release["version"], build=target_release["build"]
        )
    )
    hfs_dir_path = ""
    if sidefx_platform == "linux":
        # Unpack tar file
        with tarfile.open(houdini_installer_file_path) as tar_file:
            tar_file.extractall(downloads_dir_path)
        os.remove(houdini_installer_file_path)
        # Get folder name
        houdini_installer_dir_name = target_release_download["filename"]
        houdini_installer_dir_name = houdini_installer_dir_name.replace(".tar", "")
        houdini_installer_dir_name = houdini_installer_dir_name.replace(".gz", "")
        houdini_installer_dir_path = os.path.join(
            downloads_dir_path, houdini_installer_dir_name
        )
        cmd = [
            os.path.join(houdini_installer_dir_path, "houdini.install"),
            "--auto-install",
            "--accept-EULA",
            "2021-10-13",
            "--install-houdini",
            "--no-install-license",
            "--no-install-avahi",
            "--no-install-hqueue-server",
            "--no-install-hqueue-client",
            "--no-install-menus",
            "--no-install-bin-symlink",
            "--no-install-engine-maya",
            "--no-install-engine-unity",
            "--no-install-engine-unreal",
            "--no-install-sidefxlabs",
        ]
        status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode != 0:
            raise Exception(
                "Failed to install Houdini, ran into the following error:\n {error}".format(
                    error=status.stderr
                )
            )
        hfs_dir_path = os.path.join(
            "/opt",
            "hfs{}.{}".format(target_release["version"], target_release["build"]),
        )
        hfs_symlink_dir_path = os.path.join(os.path.dirname(hfs_dir_path), "hfs")
    elif sidefx_platform == "win64":
        cmd = [
            houdini_installer_file_path,
            "/S",
            "/AcceptEULA=2021-10-13",
            "/MainApp",
            "/LicenseServer=No",
            "/StartMenu=No",
            "/HQueueServer=No",
            "/HQueueClient=No",
            "/EngineMaya=No",
            "/Engine3dsMax",
            "/EngineUnity",
            "/EngineUnreal=No",
            "/SideFXLabs=No",
        ]
        status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode != 0:
            raise Exception(
                "Failed to install Houdini, ran into the following error:\n {error}".format(
                    error=status.stderr
                )
            )
        hfs_dir_path = os.path.join(
            "C:\Program Files\Side Effects Software",
            "Houdini {}.{}".format(target_release["version"], target_release["build"]),
        )
        hfs_symlink_dir_path = os.path.join(
            os.path.dirname(hfs_dir_path), "Houdini"
        )
    else:
        raise Exception(
            "Platform {platform} is currently not"
            "supported!".format(platform=platform)
        )
    # Create version-less symlink
    logging.info(
        "Creating symlink Houdini build {src} -> {dst}".format(
            src=hfs_dir_path, dst=hfs_symlink_dir_path
        )
    )
    os.symlink(hfs_dir_path, hfs_symlink_dir_path)


def create_sidefx_houdini_artifact(artifact_src, artifact_dst, artifact_prefix, artifact_product_name):
    """Create a .zip artifact based on the source directory content.
    The output name will have will end in the houdini build name.

    Args:
        artifact_src (str): The source directory
        artifact_dst (str): The target directory
        artifact_prefix (str): The file name prefix, the suffix will be the Houdini build name
        artifact_product_name (str): The file name product name. 
                                     This defines the Houdini product name, e.g. like houdini-py39
    Returns:
        str: The artifact file path
    """
    re_digitdot = re.compile("[^0-9.]")
    sidefx_platform = get_sidefx_platform()
    if sidefx_platform == "linux":
        hfs_build_name = os.path.basename(pathlib.Path("/opt/hfs").resolve())
    elif sidefx_platform == "win64":
        hfs_build_name = os.path.basename(
            pathlib.Path("C:\Program Files\Side Effects Software\Houdini").resolve()
        )
    else:
        raise Exception(
            "Platform {platform} is currently not"
            "supported!".format(platform=platform)
        )
    hfs_build_name = re_digitdot.sub("", hfs_build_name)
    artifact_file_path = os.path.join(
        artifact_dst, f"{artifact_prefix}_{artifact_product_name}-{hfs_build_name}-{sidefx_platform}"
    )
    artifact_dir_path = os.path.dirname(artifact_file_path)
    if not os.path.exists(artifact_dir_path):
        os.makedirs(artifact_dir_path)
    shutil.make_archive(artifact_file_path, "zip", artifact_src)


if __name__ == "__main__":


    MAYA_PYTHON_VERSION_MAPPING = {
        "2022.5": "3.9",
        "2023.3": "3.9",
        "2024.2": "3.9"
    }


    # Workspace directory
    workspace_dir_path = "/home/lucsch/Desktop/Maya"
    download_dir_path = os.path.join(workspace_dir_path, "download")
    dependency_dir_path = os.path.join(workspace_dir_path, "dependency")
    tmp_dir_path = os.path.join(workspace_dir_path, "tmp")
    #if os.path.exists(download_dir_path):
    #    shutil.rmtree(download_dir_path)
    #if os.path.exists(tmp_dir_path):
    #    shutil.rmtree(tmp_dir_path)
    if os.path.exists(dependency_dir_path):
        shutil.rmtree(dependency_dir_path)
    #os.makedirs(download_dir_path)
    #os.makedirs(tmp_dir_path)
    os.makedirs(dependency_dir_path)
    # Download
    maya_usd_sdk_source_file_path = os.path.join(download_dir_path, "maya-usd-0.27.0.zip")
    maya_usd_sdk_compiled_file_path = os.path.join(download_dir_path, "MayaUSD_0.27.0_Maya2024.2_Linux.run")

    # maya_usd_sdk_source_extracted_dir_path = os.path.join(tmp_dir_path, "usd_sdk_source")
    # maya_usd_sdk_source_dependency_dir_path = os.path.join(dependency_dir_path, "usd_sdk_source")
    maya_usd_sdk_compiled_extracted_dir_path = os.path.join(tmp_dir_path, "usd_sdk_compiled")
    maya_usd_sdk_compiled_dependency_dir_path = os.path.join(dependency_dir_path, "usd_sdk_compiled")
    maya_usd_sdk_devkit_dependency_dir_path = os.path.join(dependency_dir_path, "usd_sdk_devkit")

    autodesk_platform = get_autodesk_platform()
    if autodesk_platform == "Linux":
        # Maya USD SDK source
        # with zipfile.ZipFile(maya_usd_sdk_source_file_path, 'r') as zip_file:
        #     zip_file.extractall(maya_usd_sdk_source_extracted_dir_path)
        #     maya_usd_sdk_source_extracted_dir_path = os.path.join(maya_usd_sdk_source_extracted_dir_path, os.listdir(maya_usd_sdk_source_extracted_dir_path)[0])
        # os.rename(maya_usd_sdk_source_extracted_dir_path, maya_usd_sdk_source_dependency_dir_path)
        # Maya USD SDK compiled
        os.chmod(maya_usd_sdk_compiled_file_path, 777)
        command = [maya_usd_sdk_compiled_file_path, "--tar", "xvf", "--directory", maya_usd_sdk_compiled_extracted_dir_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        maya_usd_sdk_compiled_extracted_rpm_file_name = [f for f in os.listdir(maya_usd_sdk_compiled_extracted_dir_path) if f.endswith(".rpm")][0]
        maya_usd_sdk_compiled_extracted_rpm_file_path = os.path.join(maya_usd_sdk_compiled_extracted_dir_path, maya_usd_sdk_compiled_extracted_rpm_file_name)
        command = ["rpm", "-e", maya_usd_sdk_compiled_extracted_rpm_file_name.replace(".rpm", "")]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        command = ["rpm", "-i", "--prefix", maya_usd_sdk_compiled_extracted_dir_path, maya_usd_sdk_compiled_extracted_rpm_file_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        maya_usd_sdk_compiled_extracted_usd_dir_path = glob.glob("**{sep}mayausd{sep}USD".format(sep=os.path.sep), root_dir=maya_usd_sdk_compiled_extracted_dir_path, recursive=True)[0]
        maya_usd_sdk_compiled_extracted_usd_dir_path = os.path.join(maya_usd_sdk_compiled_extracted_dir_path, maya_usd_sdk_compiled_extracted_usd_dir_path)
        os.rename(maya_usd_sdk_compiled_extracted_usd_dir_path, maya_usd_sdk_compiled_dependency_dir_path)
        os.chmod(dependency_dir_path, 0o777)
        for root_dir_path, dir_names, file_names in os.walk(maya_usd_sdk_compiled_dependency_dir_path):
            for dir_name in dir_names:
                try:
                    os.chmod(os.path.join(root_dir_path, dir_name), 0o777)
                except:
                    pass
            for file_name in file_names:
                try:
                    os.chmod(os.path.join(root_dir_path, file_name), 0o777)
                except:
                    pass
        # Maya USD SDK devkit
        maya_usd_devkit_zip_file_path = glob.glob("**{}devkit.zip".format(os.path.sep), root_dir=maya_usd_sdk_compiled_dependency_dir_path, recursive=True)
        maya_usd_devkit_zip_file_path = os.path.join(maya_usd_sdk_compiled_dependency_dir_path, maya_usd_devkit_zip_file_path[0])
        with zipfile.ZipFile(maya_usd_devkit_zip_file_path, 'r') as zip_file:
            zip_file.extractall(maya_usd_sdk_devkit_dependency_dir_path)
        # Python


    '''
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install Houdini")
    parser.add_argument(
        "--install_houdini_product_name",
        help="Houdini product name to install. If not provided, fallback to the default.",
    )
    parser.add_argument(
        "--install_houdini_product_version",
        help="Houdini product version to install. If not provided, fallback to the latest version.",
    )
    parser.add_argument("--artifact", action="store_true", help="Create artifact")
    parser.add_argument("--artifact_src", help="Artifact source directory")
    parser.add_argument("--artifact_dst", help="Artifact target directory")
    parser.add_argument("--artifact_prefix", help="Artifact name prefix")
    parser.add_argument("--artifact_product_name", help="Artifact product name")
    args = parser.parse_args()
    # Execute
    # Install Houdini
    if args.install:
        install_sidefx_product(args.install_houdini_product_name,
                               args.install_houdini_product_version)
    # Create artifact tagged with Houdini build name (expects Houdini to be installed via the above install command)
    if args.artifact:
        create_sidefx_houdini_artifact(
            args.artifact_src, args.artifact_dst, args.artifact_prefix, args.artifact_product_name
        )
    '''