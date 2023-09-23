import argparse
import hashlib
import os
import platform
import re
import requests
import shutil
import sidefx
import subprocess
import tarfile


SIDEFX_CLIENT_ID = os.environ.get('SIDEFX_CLIENT_ID', "")
SIDEFX_CLIENT_SECRET_KEY = os.environ.get('SIDEFX_CLIENT_SECRET_KEY', "")


def create_sidefx_service(client_id, client_secret_key):
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


def get_sidefx_platform():
    """Get the active platform usable for SideFX platform API calls
    Returns:
        str: The active platform
    """
    current_platform = platform.system()
    if current_platform == 'Windows' or current_platform.startswith('CYGWIN'):
        return 'win64'
    elif current_platform == 'Darwin':
        return 'macos'
    elif current_platform == 'Linux':
        return 'linux'
    else:
        return ''


def download_sidefx_product_release(dir_path, release):
    """Download the release to the directory
    Args:
        dir_path (str): The target directory
        release (dict): The download build release dict
    Returns:
        str: The file path of the downloaded file
    """
    # Download file
    download_file_name = release['filename']
    download_file_path = os.path.join(dir_path, download_file_name)
    request = requests.get(release['download_url'], stream=True)
    if request.status_code == 200:
        with open(download_file_path, 'wb') as download_file:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, download_file)
    else:
        raise Exception('Error downloading file!')
    # Verify file checksum
    download_file_hash = hashlib.md5()
    with open(download_file_path, 'rb') as download_file:
        for chunk in iter(lambda: download_file.read(4096), b''):
            download_file_hash.update(chunk)
    if download_file_hash.hexdigest() != release['hash']:
        raise Exception('Checksum does not match!')
    return download_file_path


def install_sidefx_houdini():
    """Install the latest production release of Houdini"""
    # Connect to SideFX API
    sidefx_service = create_sidefx_service(SIDEFX_CLIENT_ID, SIDEFX_CLIENT_SECRET_KEY)
    sidefx_platform = get_sidefx_platform()
    sidefx_product = "houdini"

    # Get release data
    releases_list = sidefx_service.download.get_daily_builds_list(product=sidefx_product,
                                                                  platform=sidefx_platform,
                                                                  only_production=True)
    latest_production_release = releases_list[0]
    latest_production_release_download = sidefx_service.download.get_daily_build_download(product='houdini',
                                                                                          version=latest_production_release["version"],
                                                                                          build=latest_production_release["build"],
                                                                                          platform=sidefx_platform)


    # Download latest production release
    downloads_dir_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isdir(downloads_dir_path):
        os.makedirs(downloads_dir_path)
    houdini_installer_file_path = download_sidefx_product_release(downloads_dir_path,
                                                                  latest_production_release_download)
    # Install latest production release
    hfs_dir_path = ""
    if sidefx_platform == "linux":
        # Unpack tar file
        with tarfile.open(houdini_installer_file_path) as tar_file:
            tar_file.extractall(downloads_dir_path)
        os.remove(houdini_installer_file_path)
        # Get folder name
        houdini_installer_dir_name = houdini_installer_dir_name['filename']
        houdini_installer_dir_name = houdini_installer_dir_name.replace(".tar", "")
        houdini_installer_dir_name = houdini_installer_dir_name.replace(".gz", "")
        houdini_installer_dir_path = os.path.join(downloads_dir_path, houdini_installer_dir_name)
        cmd = [os.path.join(houdini_installer_dir_path, "houdini.install"),
               "--auto-install", "--accept-EULA", "2021-10-13",
               "--install-houdini", "--no-install-license", "--no-install-avahi",
               "--no-install-hqueue-server", "--no-install-hqueue-client", 
               "--no-install-menus", "--no-install-bin-symlink",
               "--no-install-engine-maya", "--no-install-engine-unity", "--no-install-engine-unreal", "--no-install-sidefxlabs"]
        status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode != 0:
            raise Exception("Failed to install Houdini, ran into the following error:\n {error}".format(error=status.stderr))
        hfs_dir_path = os.path.join("/opt", "hfs{}.{}".format(latest_production_release["version"],
                                                              latest_production_release["build"]))
        hfs_versionless_dir_path = os.path.join(os.path.dirname(hfs_dir_path), "hfs")
    elif sidefx_platform == "win64":
        cmd = [houdini_installer_file_path,
               "/S", "/AcceptEULA=2021-10-13",
               "/MainApp", "/LicenseServer=No", "/StartMenu=No",
               "/HQueueServer=No", "/HQueueClient=No", 
               "/EngineMaya=No", "/Engine3dsMax", "/EngineUnity", "/EngineUnreal=No", "/SideFXLabs=No"]
        status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode != 0:
            raise Exception("Failed to install Houdini, ran into the following error:\n {error}".format(error=status.stderr))
        hfs_dir_path = os.path.join("C:\Program Files\Side Effects Software", "Houdini {}.{}".format(latest_production_release["version"], latest_production_release["build"]))
        hfs_versionless_dir_path = os.path.join(os.path.dirname(hfs_dir_path), "Houdini")
    else:
        raise Exception("Platform {platform} is currently not"
                        "supported!".format(platform=platform))    
    # Create version-less symlink
    os.symlink(hfs_dir_path, hfs_versionless_dir_path)


def create_sidefx_houdini_artifact(artifact_src, artifact_dst, artifact_prefix):
    """Create a .zip artifact based on the source directory content.
    The output name will have will end in the houdini build name.

    Args:
        artifact_src (str): The source directory
        artifact_dst (str): The target directory
        artifact_prefix (str): The file name prefix, the suffix will be the Houdini build name
    Returns:
        str: The artifact file path
    """
    re_digitdot = re.compile("[^0-9.]")
    sidefx_platform = get_sidefx_platform()
    if sidefx_platform == "linux":
        hfs_build_name = os.path.basename(os.path.realpath("/opt/hfs"))
    elif sidefx_platform == "win64":
        hfs_build_name = os.path.basename(os.path.realpath("C:\Program Files\Side Effects Software\Houdini"))
    hfs_build_name = re_digitdot.sub("", hfs_build_name)
    artifact_file_path = os.path.join(artifact_dst, f"{artifact_prefix}_houdini-{hfs_build_name}-{sidefx_platform}")
    artifact_dir_path = os.path.dirname(artifact_file_path)
    if not os.path.exists(artifact_dir_path):
        os.makedirs(artifact_dir_path)
    shutil.make_archive(artifact_file_path, 'zip', artifact_src)


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true', help='Install Houdini')
    parser.add_argument('--artifact', action='store_true', help='Create artifact')
    parser.add_argument('--artifact_src', help='Artifact source directory')
    parser.add_argument('--artifact_dst', help='Artifact target directory')
    parser.add_argument('--artifact_prefix', help='Artifact name prefix')
    args = parser.parse_args()
    # Execute
    # Install Houdini
    if args.install:
        install_sidefx_houdini()
    # Create artifact tagged with Houdini build name (expects Houdini to be installed via the above install command)
    if args.artifact:
        create_sidefx_houdini_artifact(args.artifact_src, args.artifact_dst, args.artifact_prefix)