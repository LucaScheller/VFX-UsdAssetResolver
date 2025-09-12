import argparse
import logging
import os
import pathlib
import platform
import re
import shutil
import stat
import subprocess
from typing import Literal, Union

import requests
import sidefx

SIDEFX_CLIENT_ID = os.environ.get("SIDEFX_CLIENT_ID", "")
SIDEFX_CLIENT_SECRET_KEY = os.environ.get("SIDEFX_CLIENT_SECRET_KEY", "")


logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")


def create_sidefx_service(client_id: str, client_secret_key: str):
    """Get the SideFX API service
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


def get_sidefx_platform() -> Union[Literal["win64"], Literal["macos"], Literal["linux"]]:
    """Get the active platform usable for SideFX platform API calls
    Returns:
        str: The active platform
    """
    current_platform = platform.system()
    if current_platform == "Windows" or current_platform.startswith("CYGWIN"):
        return "win64"
    elif current_platform == "Darwin":
        return "macos"
    elif current_platform == "Linux":
        return "linux"
    raise Exception(f"Platform not supported: {current_platform}")


def download_sidefx_product_release(dir_path: str, release: dict) -> str:
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
    os.chmod(
        download_file_path,
        stat.ST_MODE
        | stat.S_IEXEC
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IRUSR
        | stat.S_IRGRP,
    )

    return download_file_path


def install_sidefx_product(product: str, version: str) -> None:
    """Install a production release of Houdini
    Args:
        product (str): The target product name (e.g. houdini, houdini-py39, etc.)
        version (str|None): The target product version (e.g. 20.0, 19.5, etc.)
    """

    # Create downloads directory
    downloads_dir_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isdir(downloads_dir_path):
        os.makedirs(downloads_dir_path)

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
            if float(release["version"]) >= 20.0:
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
            "No Houdini version found for requested version | {}".format(version)
        )

    # Install Houdini through launcher
    logging.info("Downloading Houdini Launcher")

    houdini_launcher_releases_list = sidefx_service.download.get_daily_builds_list(
        product="houdini-launcher",
        version=None,
        platform=sidefx_platform,
        only_production=True,
    )
    if not houdini_launcher_releases_list:
        raise Exception("No 'houdini-launcher' releases found!")

    houdini_launcher_target_release = houdini_launcher_releases_list[0]
    houdini_launcher_target_release_download = (
        sidefx_service.download.get_daily_build_download(
            product=houdini_launcher_target_release["product"],
            version=houdini_launcher_target_release["version"],
            build=houdini_launcher_target_release["build"],
            platform=houdini_launcher_target_release["platform"],
        )
    )

    houdini_launcher_installer_file_path = download_sidefx_product_release(
        downloads_dir_path, houdini_launcher_target_release_download
    )

    license_file_path = os.path.join(downloads_dir_path, "sidefx_settings.ini")
    with open(license_file_path, "w") as license_file:
        license_file.write(
            f"client_id={SIDEFX_CLIENT_ID}\nclient_secret={SIDEFX_CLIENT_SECRET_KEY}\n"
        )

    # Currently the API and the installer consume different syntaxes for product and build option
    cmd_flags = ["install"]
    if "-" in target_release["product"]:
        target_release_product, target_release_build_type = target_release[
            "product"
        ].split("-")
        cmd_flags.extend(
            [
                "--product",
                target_release_product,
                "--build-option",
                target_release_build_type,
            ]
        )
    else:
        cmd_flags.extend(["--product", target_release["product"]])
    cmd_flags.extend(
        [
            "--version",
            f"{target_release['version']}.{target_release['build']}",
            "--platform",
            target_release["platform"],
            "--settings-file",
            license_file_path,
            "--accept-EULA",
            "SideFX-2021-10-13",
        ]
    )
    hfs_dir_path = ""
    if sidefx_platform == "linux":
        cmd = [houdini_launcher_installer_file_path]
        status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode != 0:
            raise Exception(
                "Failed to install Houdini Launcher, ran into the following error:\n {error}".format(
                    error=status.stderr
                )
            )
        logging.info(
            "Installing Houdini build {version}.{build}".format(
                version=target_release["version"], build=target_release["build"]
            )
        )
        cmd = ["/opt/sidefx/launcher/bin/houdini_installer"]
        cmd.extend(cmd_flags)
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
        status = subprocess.run(
            [houdini_launcher_installer_file_path, "/S"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if status.returncode != 0:
            raise Exception(
                "Failed to install Houdini Launcher, ran into the following error:\n {error}".format(
                    error=status.stderr
                )
            )
        logging.info(
            "Installing Houdini build {version}.{build}".format(
                version=target_release["version"], build=target_release["build"]
            )
        )
        cmd = [r"C:\Program Files\SideFX\launcher\bin\houdini_installer.exe"]
        cmd.extend(cmd_flags)
        status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode != 0:
            raise Exception(
                "Failed to install Houdini, ran into the following error:\n {error}".format(
                    error=status.stderr
                )
            )
        hfs_dir_path = os.path.join(
            r"C:\Program Files\Side Effects Software",
            "Houdini {}.{}".format(target_release["version"], target_release["build"]),
        )
        hfs_symlink_dir_path = os.path.join(os.path.dirname(hfs_dir_path), "Houdini")
    else:
        raise Exception(
            "Platform {platform} is currently not supported!".format(platform=platform)
        )
    # Create version-less symlink
    logging.info(
        "Creating symlink Houdini build {src} -> {dst}".format(
            src=hfs_dir_path, dst=hfs_symlink_dir_path
        )
    )
    os.symlink(hfs_dir_path, hfs_symlink_dir_path)


def create_sidefx_houdini_artifact(
    artifact_src: str,
    artifact_dst: str,
    artifact_prefix: str,
    artifact_product_name: str,
) -> None:
    """Create a .zip artifact based on the source directory content.
    The output name will have will end in the houdini build name.

    Args:
        artifact_src (str): The source directory
        artifact_dst (str): The target directory
        artifact_prefix (str): The file name prefix, the suffix will be the Houdini build name
        artifact_product_name (str): The file name product name.
                                     This defines the Houdini product name, e.g. like 'houdini-py39'
    Returns:
        str: The artifact file path
    """
    re_digitdot = re.compile("[^0-9.]")
    sidefx_platform = get_sidefx_platform()
    if sidefx_platform == "linux":
        hfs_build_name = os.path.basename(pathlib.Path("/opt/hfs").resolve())
    elif sidefx_platform == "win64":
        hfs_build_name = os.path.basename(
            pathlib.Path(r"C:\Program Files\Side Effects Software\Houdini").resolve()
        )
    else:
        raise Exception(
            "Platform {platform} is currently notsupported!".format(platform=platform)
        )
    hfs_build_name = re_digitdot.sub("", hfs_build_name)
    artifact_file_path = os.path.join(
        artifact_dst,
        f"{artifact_prefix}_{artifact_product_name}-{hfs_build_name}-{sidefx_platform}",
    )
    artifact_dir_path = os.path.dirname(artifact_file_path)
    if not os.path.exists(artifact_dir_path):
        os.makedirs(artifact_dir_path)
    shutil.make_archive(artifact_file_path, "zip", artifact_src)


if __name__ == "__main__":
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
        install_sidefx_product(
            args.install_houdini_product_name, args.install_houdini_product_version
        )
    # Create artifact tagged with Houdini build name (expects Houdini to be installed via the above install command)
    if args.artifact:
        create_sidefx_houdini_artifact(
            args.artifact_src,
            args.artifact_dst,
            args.artifact_prefix,
            args.artifact_product_name,
        )
