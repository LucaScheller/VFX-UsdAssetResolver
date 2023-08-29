import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
import argparse
import requests
import sidefx

SIDEFX_CLIENT_ID = os.environ['SIDEFX_CLIENT_ID']
SIDEFX_CLIENT_SECRET_KEY = os.environ['SIDEFX_CLIENT_SECRET_KEY']


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
        string: The active platform
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
        folder_dir_path: The folder dir path of the unpacked tar file
    """
    # Download tar file
    tar_file_name = release['filename']
    tar_file_path = os.path.join(dir_path, tar_file_name)
    request = requests.get(release['download_url'], stream=True)
    if request.status_code == 200:
        with open(tar_file_path, 'wb') as tar_file:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, tar_file)
    else:
        raise Exception('Error downloading file!')
    # Verify tar file checksum
    tar_file_hash = hashlib.md5()
    with open(tar_file_path, 'rb') as tar_file:
        for chunk in iter(lambda: tar_file.read(4096), b''):
            tar_file_hash.update(chunk)
    if tar_file_hash.hexdigest() != release['hash']:
        raise Exception('Checksum does not match!')
    # Unpack tar file
    with tarfile.open(tar_file_path) as tar_file:
        tar_file.extractall(dir_path)
    os.remove(tar_file_path)
    # Get folder name
    product_release_folder_name = tar_file_name
    product_release_folder_name = product_release_folder_name.replace(".tar", "")
    product_release_folder_name = product_release_folder_name.replace(".gz", "")
    return os.path.join(dir_path, product_release_folder_name)


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
    houdini_installer_dir_path = download_sidefx_product_release(downloads_dir_path,
                                                                 latest_production_release_download)
    # Install latest production release
    hfs_dir_path = ""
    if sidefx_platform == "linux":
        houdini_installer_dir_path = "/root/Downloads/houdini-19.5.716-linux_x86_64_gcc9.3"
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
    else:
        raise Exception("Platform {platform} is currently not"
                        "supported!".format(platform=platform))    
    # Create version-less symlink
    hfs_version_less_dir_path = os.path.join(os.path.dirname(hfs_dir_path), "hfs")
    os.symlink(hfs_dir_path, hfs_version_less_dir_path)


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--houdini_install', action='store_true', help='Install Houdini')
    parser.add_argument('--resolver_build', action='store_true', help='Build USD Asset Resolvers')
    args = parser.parse_args()
    # Execute
    if args.houdini_install:
        # Install Houdini
        install_sidefx_houdini()
    elif args.resolver_build:
        # Build resolvers
        pass