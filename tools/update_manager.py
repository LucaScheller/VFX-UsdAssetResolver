import contextlib
import json
import os
import platform
import re
import shutil
import ssl
import sys
import tempfile
import zipfile
from urllib import request

from PySide2 import QtCore, QtGui, QtWidgets

# To run, execute this in the Houdini/Maya
"""
import ssl; from urllib import request
update_manager_url = 'https://raw.githubusercontent.com/LucaScheller/VFX-UsdAssetResolver/main/tools/update_manager.py?token=$(date+%s)'
exec(request.urlopen(update_manager_url,context=ssl._create_unverified_context()).read(), globals(), locals())
run_dcc()
"""

REPO_URL = "https://api.github.com/repos/lucascheller/VFX-UsdAssetResolver"
RELEASE_INSTALL_DIRECTORY_PREFIX = "UsdAssetResolver_v"
ENV_USD_ASSET_RESOLVER = "USD_ASSET_RESOLVER"
HOUDINI_PACKAGE_FILE_NAME = "UsdAssetResolver.json"
HOUDINI_RELEASE_ASSET_ELEMENTS_REGEX = re.compile(
    "UsdAssetResolver_(houdini)(-py[0-9]+)?-([0-9.]+)-(linux|win64).zip"
)
MAYA_RELEASE_ASSET_ELEMENTS_REGEX = re.compile(
    "UsdAssetResolver_(maya)-([0-9.]+)-USD-SDK-([0-9.]+)-(Linux|Windows).zip"
)
QT_WINDOW_TITLE = "USD Asset Resolver - Update Manager"
QT_ROLE_RELEASE = QtCore.Qt.UserRole + 1001


class ZipFileWithPermissions(zipfile.ZipFile):
    """Custom ZipFile class handling file permissions.
    See https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries
    """

    def _extract_member(self, member, target_path, pwd):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)
        target_path = super()._extract_member(member, target_path, pwd)
        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(target_path, attr)
        return target_path


class UpdateManagerUI(QtWidgets.QDialog):
    def __init__(self):
        super(UpdateManagerUI, self).__init__()

        # Window settings
        self.setWindowTitle(QT_WINDOW_TITLE)
        self.setMinimumWidth(500)
        self.setStyleSheet(
            "QWidget {background-color:hsl(0,0,60);} QGroupBox {border: 2px solid rgb(0,208,255);}"
        )

        # Update manager
        self.update_manager = UpdateManager()

        # Setup and initialize UI
        self.setup_widgets()
        self.setup_layouts()
        self.setup_signals()
        self.initialize()

    def setup_widgets(self):
        """Setup UI widgets"""
        # Directory
        self.directory_label = QtWidgets.QLabel("Directory")
        self.directory_lineedit = QtWidgets.QLineEdit()
        self.directory_lineedit.setPlaceholderText("Installation Directory")
        self.directory_browse_button = QtWidgets.QPushButton("Browse")
        # Release
        self.release_label = QtWidgets.QLabel("Release")
        self.release_combobox = QtWidgets.QComboBox()
        # Resolver
        self.resolver_label = QtWidgets.QLabel("Resolver")
        self.resolver_combobox = QtWidgets.QComboBox()
        # Preferences
        self.preferences_group_box = QtWidgets.QGroupBox("Installation Preferences")
        # Install / Uninstall
        self.install_button = QtWidgets.QPushButton("Install")
        self.uninstall_button = QtWidgets.QPushButton("Uninstall / Change Release")

    def setup_layouts(self):
        """Setup layout"""
        # Directory
        directory_layout = QtWidgets.QHBoxLayout()
        directory_layout.addWidget(self.directory_label)
        directory_layout.addWidget(self.directory_lineedit)
        directory_layout.addWidget(self.directory_browse_button)
        # Release
        release_layout = QtWidgets.QHBoxLayout()
        release_layout.addWidget(self.release_label)
        release_layout.addWidget(self.release_combobox)
        # Resolver
        resolver_layout = QtWidgets.QHBoxLayout()
        resolver_layout.addWidget(self.resolver_label)
        resolver_layout.addWidget(self.resolver_combobox)
        # Preferences
        preferences_layout = QtWidgets.QVBoxLayout()
        preferences_layout.addLayout(directory_layout)
        preferences_layout.addLayout(release_layout)
        preferences_layout.addLayout(resolver_layout)
        self.preferences_group_box.setLayout(preferences_layout)

        # Main layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.preferences_group_box)
        layout.addWidget(QtWidgets.QLabel("", self))
        layout.addWidget(self.install_button)
        layout.addWidget(self.uninstall_button)

    def setup_signals(self):
        """Setup signal/slots"""
        # Directory
        self.directory_lineedit.editingFinished.connect(
            self.directory_lineedit_editingFinished
        )
        self.directory_browse_button.clicked.connect(
            self.directory_browse_button_clicked
        )
        # Release
        self.release_combobox.currentTextChanged.connect(
            self.release_combobox_currentTextChanged
        )
        # Install
        self.install_button.clicked.connect(self.install_button_clicked)
        self.uninstall_button.clicked.connect(self.uninstall_button_clicked)

    def initialize(self):
        """Initialize the UI based on the active software and platform"""
        # Mode
        plugin_dir_path = os.environ.get(ENV_USD_ASSET_RESOLVER)
        plugin_loaded = bool(plugin_dir_path)
        self.preferences_group_box.setEnabled(not plugin_loaded)
        self.install_button.setVisible(not plugin_loaded)
        self.uninstall_button.setVisible(plugin_loaded)
        if plugin_loaded:
            self.directory_lineedit.setText(plugin_dir_path)
            self.release_label.setVisible(False)
            self.release_combobox.setVisible(False)
            self.resolver_label.setVisible(False)
            self.resolver_combobox.setVisible(False)
            self.uninstall_button.setVisible(True)
        else:
            self.release_label.setVisible(True)
            self.release_combobox.setVisible(True)
            self.resolver_label.setVisible(True)
            self.resolver_combobox.setVisible(True)
            self.uninstall_button.setVisible(False)
            # Query data
            self.update_manager.initialize()
            # Update UI
            for release in self.update_manager.releases:
                release_name = release["name"]
                item = QtGui.QStandardItem(release_name)
                item.setData(release, QT_ROLE_RELEASE)
                self.release_combobox.model().appendRow(item)
            if not self.update_manager.releases:
                self.install_button.setEnabled(False)

    def directory_lineedit_editingFinished(self):
        """Validate the directory path"""
        directory_path = self.directory_lineedit.text()
        self.directory_lineedit.setText(
            directory_path if directory_path[-1] != "/" else directory_path[:-1]
        )

    def directory_browse_button_clicked(self):
        """Browse to a custom directory"""
        dir_path = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory", self.directory_lineedit.text()
            )
        )
        self.directory_lineedit.setText(dir_path)
        self.release_combobox_currentTextChanged()

    def release_combobox_currentTextChanged(self):
        """Validate the install directory based on the selected release version"""
        dir_path = self.directory_lineedit.text()
        if not dir_path:
            dir_path = os.path.join(os.path.expanduser("~"), "Desktop")
        release_data = self.release_combobox.currentData(QT_ROLE_RELEASE)
        if not release_data:
            return
        # Conform install directory
        dir_name = "{}{}".format(
            RELEASE_INSTALL_DIRECTORY_PREFIX,
            release_data["name"][1:],
        )
        if not os.path.basename(dir_path).startswith(RELEASE_INSTALL_DIRECTORY_PREFIX):
            dir_path = os.path.join(dir_path, dir_name)
        else:
            dir_path = os.path.join(os.path.dirname(dir_path), dir_name)
        self.directory_lineedit.setText(dir_path)
        # Load resolvers
        active_resolver = self.resolver_combobox.currentText()
        self.resolver_combobox.clear()
        self.resolver_combobox.addItems(release_data["resolvers"])
        self.resolver_combobox.setCurrentIndex(
            max(0, self.resolver_combobox.findText(active_resolver))
        )

    def install_button_clicked(self):
        # Install
        download_url = self.release_combobox.currentData(QT_ROLE_RELEASE)["url"]
        install_dir_path = self.directory_lineedit.text()
        resolve_name = self.resolver_combobox.currentText()
        self.update_manager.install_release(
            self.update_manager.platform,
            self.update_manager.product_name,
            self.update_manager.product_version,
            download_url,
            install_dir_path,
            resolve_name,
        )
        # Message
        self.close()
        QtWidgets.QMessageBox.information(
            self,
            QT_WINDOW_TITLE,
            "Installation successfull.\n"
            "Please restart the application by launching it via the 'launcher.bat/.sh' file "
            "in your chosen install directory at '{install_dir_path}'.".format(
                install_dir_path=install_dir_path
            ),
        )

    def uninstall_button_clicked(self):
        install_dir_path = os.environ[ENV_USD_ASSET_RESOLVER]
        answer = QtWidgets.QMessageBox.warning(
            self,
            QT_WINDOW_TITLE,
            "The following folder will be removed: {}".format(install_dir_path),
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
        )

        if answer == QtWidgets.QMessageBox.Ok:
            self.update_manager.release_uninstall(install_dir_path)
            self.close()

            answer = QtWidgets.QMessageBox.information(
                self,
                QT_WINDOW_TITLE,
                "Uninstall successful. Please restart the application.\nDo you want to alternatively reinstall a different release? ",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel,
            )
            if answer == QtWidgets.QMessageBox.Yes:
                run_dcc()


class UpdateManager(object):
    def __init__(self):
        self.platform = ""
        self.product_name = ""
        self.product_version = ""
        self.product_python_version = ""
        self.releases = []

    def initialize(self):
        self.platform = self.get_platform()
        self.product_name, self.product_version, self.product_python_version = (
            self.get_software()
        )
        self.releases = self.get_release_data(
            self.platform,
            self.product_name,
            self.product_version,
            self.product_python_version,
        )

    def get_platform(self):
        """Get the active platform
        Returns:
            str: The active platform
        """
        current_platform = platform.system()
        if current_platform == "Windows" or current_platform.startswith("CYGWIN"):
            return "windows"
        elif current_platform == "Darwin":
            return "macos"
        elif current_platform == "Linux":
            return "linux"
        else:
            return ""

    def get_dcc_name(self):
        """Get the active dcc
        Returns:
            str: The active dcc
        """
        # Houdini
        try:
            import hou

            if not hou.isUIAvailable():
                raise ImportError
            return "houdini"
        except Exception:
            pass
        # Maya
        try:
            import pymel.core as pm

            return "maya"
        except Exception:
            pass

        raise Exception(
            "This function can only be run in an active DCC session."
            "Currently support are Houdini and Maya."
        )

    def get_software(self):
        """Get the active software
        Returns:
            str: The active software name
            str: The active software version
            str: The active software python version
        """
        product_name = "<undefined>"
        product_version = "<undefined>"
        product_python_version = "<undefined>"
        dcc_name = self.get_dcc_name()
        if dcc_name == "houdini":
            import hou

            product_name = "houdini"
            product_version = hou.applicationVersionString()
            product_python_version = "-py{}{}".format(
                sys.version_info.major, str(sys.version_info.minor)[:1]
            )
        elif dcc_name == "maya":
            from pymel import versions as pymel_versions

            product_name = "maya"
            product_version = pymel_versions.shortName
            product_python_version = ""

        return product_name, product_version, product_python_version

    def get_software_houdini_version_match(self, active_version, target_version):
        """Check if the active version is compatible with the target version.
        Currently this just assumes that major/minor release versions use are USD API/ABI compatible.
        Args:
            active_version(str): The active software version string
            target_version(str): The target software version string
        Returns:
            bool: The match state
        """
        active_version = [int(v) for v in (active_version.split(".") + ["0"] * 3)[:3]]
        target_version = [int(v) for v in (target_version.split(".") + ["0"] * 3)[:3]]
        # Major version
        if active_version[0] != target_version[0]:
            return False
        # Minor version
        if active_version[1] != target_version[1]:
            return False
        # Build version
        # if active_version[2] != target_version[2]:
        #     return False
        return True

    def get_software_maya_version_match(self, active_version, target_version):
        """Check if the active version is compatible with the target version.
        Currently this just assumes that major/minor release versions use are USD API/ABI compatible.
        Args:
            active_version(str): The active software version string
            target_version(str): The target software version string
        Returns:
            bool: The match state
        """
        target_version = target_version.split(".")[0]
        # Major version
        if active_version != target_version:
            return False
        return True

    def get_release_data(
        self, platform_name, product_name, product_version, product_python_version
    ):
        """Get release data via GitHub API
        Args:
            platform_name(str): The OS.
            product_name(str): The software name ('houdini' or 'maya')
            product_version(str): The software version string.
                                  Only exact matches and major version matches are considered.
            product_python_version (str): The python version string in the form of '-py39', '-py37', etc.
        Returns:
            list: A list of release dicts ({"name": "v0.1", "resolvers": ["fileResolver"], "url": "https://download.zip"}) that match the input query
        """
        # Query release data
        try:
            with contextlib.closing(
                request.urlopen(
                    request.Request(REPO_URL + "/releases"),
                    context=ssl._create_unverified_context(),
                )
            ) as response:
                data = json.loads(response.read())
        except Exception:
            data = []

        dcc_vendor_platform_mapping = {
            "houdini": {"windows": "win64", "macos": "macos", "linux": "linux"},
            "maya": {"windows": "Windows", "macos": "MacOS", "linux": "Linux"},
        }

        # Extract relevant data
        filtered_data = {}
        for release in data:
            # Skip pre releases
            if release["prerelease"]:
                continue
            resolvers = None
            for asset in release["assets"]:
                if asset["content_type"] != "application/zip":
                    continue
                asset_name = asset["name"]
                asset_product_python_version = ""
                asset_product_sdk_version = ""
                if product_name == "houdini":
                    asset_name_elements = HOUDINI_RELEASE_ASSET_ELEMENTS_REGEX.match(asset_name)
                    if not asset_name_elements:
                        continue
                    (
                        asset_product_name,
                        asset_product_python_version,
                        asset_product_version,
                        asset_platform,
                    ) = asset_name_elements.groups()
                elif product_name == "maya":
                    asset_name_elements = MAYA_RELEASE_ASSET_ELEMENTS_REGEX.match(asset_name)
                    if not asset_name_elements:
                        continue
                    (
                        asset_product_name,
                        asset_product_version,
                        asset_product_sdk_version,
                        asset_platform,
                    ) = asset_name_elements.groups()
                if asset_platform != dcc_vendor_platform_mapping[product_name][platform_name]:
                    continue
                if product_name == "houdini":
                    if not self.get_software_houdini_version_match(
                        product_version, asset_product_version
                    ):
                        continue
                elif product_name == "maya":
                    if not self.get_software_maya_version_match(
                        product_version, asset_product_version
                    ):
                        continue
                else:
                    continue
                asset_url = asset["browser_download_url"]
                # Since we don't track via metadata what resolvers are stored per release,
                # we have to inspect each release.
                # ToDo Refactor this to use release message or other mechanism.
                # We only parse this once per release as each release has the same resolvers.
                if resolvers is None:
                    with tempfile.TemporaryDirectory() as tmp_dir_path:
                        asset_file_path = os.path.join(tmp_dir_path, asset_name)
                        asset_file_content = request.urlopen(
                            asset_url, context=ssl._create_unverified_context()
                        )
                        with open(asset_file_path, "wb") as asset_file:
                            asset_file.write(asset_file_content.read())
                        # Inspect archive
                        with zipfile.ZipFile(asset_file_path, "r") as asset_zip_file:
                            resolvers = []
                            for asset_zip_path in zipfile.Path(
                                asset_zip_file
                            ).iterdir():
                                resolvers.append(asset_zip_path.name)
                if not resolvers:
                    resolvers = None
                    continue
                # Only collect the first possible match
                filtered_data.setdefault(release["name"], {})
                filtered_data[release["name"]].setdefault(asset_product_version, {})
                filtered_data[release["name"]][asset_product_version][
                    asset_product_python_version or "__default__"
                ] = {
                    "name": release["name"],
                    "resolvers": resolvers,
                    "url": asset_url,
                    "product_python_version": asset_product_python_version,
                    "product_sdk_version": asset_product_sdk_version,
                    "product_version": asset_product_version,
                }

        # Prefer exact Python version matches over inferred matches
        latest_filtered_data = []
        for release_name, release_product_versions in filtered_data.items():
            latest_release_product_version = release_product_versions[
                sorted(release_product_versions.keys(), reverse=True)[0]
            ]
            latest_filtered_data.append(
                latest_release_product_version.get(
                    product_python_version,
                    latest_release_product_version["__default__"],
                )
            )
        return latest_filtered_data

    def download_file(self, url, file_path):
        """Download file at the given url to the given file path
        Args:
            url(str): The url to download from
            file_path(str): The file path to download to
        Returns:
            str: The file path of the downloaded file
        """
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        try:
            file_content = request.urlopen(
                url, context=ssl._create_unverified_context()
            )
            with open(file_path, "wb") as output:
                output.write(file_content.read())
        except:
            raise ValueError("Unable to download file: {}".format(url))

        return file_path

    def uncompress_file(self, file_path, compression_type="zip"):
        """Uncompress the given archive in place.
        Args:
            file_path(str): The file path to the file to uncompress
            archive_type(str): The compression type
        Returns:
            str: The directory path to the uncompressed file
        """
        if compression_type == "zip":
            # Extract Archive
            dir_path = os.path.join(
                os.path.dirname(file_path),
                os.path.basename(file_path).replace(".zip", ""),
            )
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with ZipFileWithPermissions(
                file_path, "r", zipfile.ZIP_DEFLATED
            ) as archive:
                archive.extractall(dir_path)
            os.remove(file_path)
        else:
            raise Exception(
                "The given compression type is not supported: {}".format(
                    compression_type
                )
            )

        return dir_path

    def install_release(
        self,
        platform_name,
        product_name,
        product_version,
        download_url,
        directory_path,
        resolver_name,
    ):
        """Download and install the given release.
        # ToDo Instead of using 'HFS' for the Houdini install directory, use the software version input arg.
        Args:
            platform_name(str): The active platform
            product_name(str): The software name
            product_version(str): The software version
            download_url(str): The download url
            directory_path(str): The directory to download the resolvers to
            resolver_name(str): The resolver name to initialize
        """
        download_file_path = self.download_file(
            download_url, "{}.{}".format(directory_path, "zip")
        )
        directory_path = self.uncompress_file(download_file_path)
        resolver_dir_path = os.path.join(directory_path, resolver_name)
        # Cleanup other resolvers
        for dir_name in os.listdir(directory_path):
            if dir_name != resolver_name:
                shutil.rmtree(os.path.join(directory_path, dir_name))
        # Build launcher
        env = {
            "PXR_PLUGINPATH_NAME": os.path.join(resolver_dir_path, "resources"),
            "PYTHONPATH": os.path.join(resolver_dir_path, "lib", "python"),
        }
        if resolver_name in ["PythonResolver", "CachedResolver"]:
            env.update(
                {
                    "AR_ENV_SEARCH_PATHS": "{}{}{}".format(
                        "/change/this/path/to/shots",
                        os.pathsep,
                        "/change/this/path/to/assets",
                    ),
                    "AR_ENV_SEARCH_REGEX_EXPRESSION": "(v\d\d\d)",
                    "AR_ENV_SEARCH_REGEX_FORMAT": "v000",
                }
            )

        if platform_name == "linux":
            env["LD_LIBRARY_PATH"] = os.path.join(resolver_dir_path, "lib")
            launch_file_path = os.path.join(directory_path, "launch.sh")
            with open(launch_file_path, "w") as launch_file:
                lines = []
                lines.append("#!/bin/bash")
                # Environment
                lines.append("# Setup environment")
                # UpdateManager
                lines.append(
                    "export {}={}".format(ENV_USD_ASSET_RESOLVER, directory_path)
                )
                # Debug
                lines.append("export {}={}".format("TF_DEBUG", "AR_RESOLVER_INIT"))
                # Env
                for env_name, env_value in sorted(env.items(), key=lambda k: k[0]):
                    lines.append(
                        "export {env_name}={env_value}{sep}${env_name}".format(
                            env_name=env_name, env_value=env_value, sep=os.pathsep
                        )
                    )
                if product_name == "houdini":
                    # App
                    lines.append("# Launch Houdini")
                    lines.append(
                        "pushd {} && source houdini_setup && popd".format(
                            os.environ["HFS"]
                        )
                    )
                    # Command
                    lines.append('houdini -foreground "$@"')
                    launch_file.writelines(line + "\n" for line in lines)
                elif product_name == "maya":
                    # App
                    lines.append("# Launch Maya")
                    # Command
                    lines.append('{} "$@"'.format(os.path.join(os.environ["MAYA_LOCATION"], "bin", "maya")))
                    launch_file.writelines(line + "\n" for line in lines)
            # Make executable
            os.chmod(launch_file_path, 0o0777)
        elif platform_name == "windows":
            env["PATH"] = os.path.join(resolver_dir_path, "lib")
            launch_file_path = os.path.join(directory_path, "launch.bat")
            with open(launch_file_path, "w") as launch_file:
                lines = []
                # Environment
                lines.append("REM Setup environment")
                # UpdateManager
                lines.append(
                    "set {}={}".format(ENV_USD_ASSET_RESOLVER, directory_path)
                )
                # Debug
                lines.append("set {}={}".format("TF_DEBUG", "AR_RESOLVER_INIT"))
                # Env
                for env_name, env_value in sorted(env.items(), key=lambda k: k[0]):
                    lines.append(
                        "set {env_name}={env_value}{sep}%{env_name}%".format(
                            env_name=env_name, env_value=env_value, sep=os.pathsep
                        )
                    )
                # App & command
                if product_name == "houdini":
                    lines.append("REM Launch Houdini")
                    lines.append(os.path.join(os.environ["HFS"], "bin", "houdini"))
                    launch_file.writelines(line + "\n" for line in lines)
                elif product_name == "maya":
                    lines.append("REM Launch Maya")
                    lines.append(os.path.join(os.environ["MAYA_LOCATION"], "bin", "maya"))
                    launch_file.writelines(line + "\n" for line in lines)
            # Make executable
            os.chmod(launch_file_path, 0o0777)
        else:
            raise Exception(
                "Platform {} is currently not supported!".format(platform_name)
            )
        # Houdini Packages
        # # This currently doesn't work because packages are processed after startup (after USD is initialized)
        # package_content = { "env" : [{ ENV_USD_ASSET_RESOLVER : directory_path},
        #                              { "PXR_PLUGINPATH_NAME" : os.path.join(resolver_dir_path, "resources")},
        #                              { "PYTHONPATH" : os.path.join(resolver_dir_path, "lib", "python")},
        #                              { "LD_LIBRARY_PATH" : os.path.join(resolver_dir_path, "lib")},
        #                              { "TF_DEBUG" : "AR_RESOLVER_INIT"}]}
        # if platform_name == "win64":
        #     package_content["env"].append({"PATH": os.path.join(resolver_dir_path, "lib")})
        # hou_user_pref_dir_path = os.environ["HOUDINI_USER_PREF_DIR"]
        # hou_packages_dir_path = os.path.join(hou_user_pref_dir_path, "packages")
        # hou_package_file_path = os.path.join(hou_packages_dir_path, HOUDINI_PACKAGE_FILE_NAME)
        # # This doesn't work for language specific user folders
        # # ToDo Find a platform agnostic way to do this
        # # if platform_name == "win64":
        # #     hou_user_pref_dir_path = os.path.join(os.path.expanduser("~"), "Documents",
        # #                                           "houdini{}".format(".".join(product_version.split("."[:2]))))
        # #     hou_packages_dir_path = os.path.join(hou_user_pref_dir_path, "packages")
        # # elif platform_name == "linux":
        # #     hou_user_pref_dir_path = os.path.join(os.path.expanduser("~"),
        # #                                           "houdini{}".format(".".join(product_version.split("."[:2]))))
        # #     hou_packages_dir_path = os.path.join(hou_user_pref_dir_path, "packages")
        # # else:
        # #     raise Exception("Platform {} is currently not supported!".format(platform))
        # if not os.path.exists(hou_packages_dir_path):
        #     os.makedirs(hou_packages_dir_path)
        # with open(hou_package_file_path, "w") as hou_package_file:
        #     json.dump(package_content, hou_package_file, indent=4)

        # This protects against running the updated multiple times in the same session.
        os.environ[ENV_USD_ASSET_RESOLVER] = directory_path

    def release_uninstall(self, directory_path):
        """Peform an uninstall
        Args:
            directory_path(str): The directory path to uninstall and remove
        """
        shutil.rmtree(directory_path)
        del os.environ[ENV_USD_ASSET_RESOLVER]


def run_dcc():
    """Run the Update Manager in a DCC"""

    dialog = UpdateManagerUI()
    dialog.exec_()
