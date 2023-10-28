import contextlib
import json
import os
import platform
import re
import shutil
import ssl
import subprocess
import tempfile
import urllib
import zipfile
from urllib import request

def install_side_effect_httpResolver(platform_name, software_name, resolver_dir_path):
    """The install side effect for the httpResolver.
    # ToDo Instead of using 'HFS' for the Houdini install directory, add a software version input arg.
    This does the following:
    - Create a venv in the ./demo folder
    - Install fastapi
    Args:
        platform_name(str): The active platform
        directory_path(str): The resolver directory path
    Returns:
        str: A command to run before app execution
    """
    # Validate
    if platform_name == "macos":
        raise Exception(
            "Platform {} is currently not supported!".format(platform_name)
        )


    demo_dir_path = os.path.join(resolver_dir_path, "demo")
    python_exe = os.path.join(os.environ["HFS"], "python", "bin", "python")

    # Create venv
    subprocess.check_call([python_exe, "-m", "venv", "venv"], cwd=demo_dir_path)
    venv_python_exe = os.path.join(demo_dir_path, "venv", "bin", "python")
    # Install deps (We can't use the pyproject.toml as it depends on .git)
    subprocess.check_call([venv_python_exe, "-m", "pip", "install", "fastapi[all]"], cwd=demo_dir_path)
    # Command
    if platform_name == "linux":
        command = "uvicorn arHttpSampleServer:app --reload &"
    elif platform_name == "win64":
        command = ""
    return command


install_side_effect_httpResolver("", "", "/mnt/data/PROJECT/VFX-UsdAssetResolver/dist/httpResolver")