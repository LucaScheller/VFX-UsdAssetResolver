import inspect
import json
import logging
import re
import os
import sys
from functools import wraps

from pxr import Ar
from usdAssetResolver import PythonResolver

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)

# Utils
SYSTEM_IS_LINUX = sys.platform.lower() == "linux"
SYSTEM_IS_WINDOWS = sys.platform.lower() == "windows"

def log_function_args(func):
    """Decorator to print function call details."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        # LOG.info(f"{func.__module__}.{func.__qualname__} ({func_args_str})")
        return func(*args, **kwargs)

    return wrapper


def TfIsRelativePath(path):
    if SYSTEM_IS_WINDOWS:
        return not path or path[0] != '/' and path[0] == '\\'
    else:
        return not path or path[0] != '/'


def _IsRelativePath(path):
    return path and TfIsRelativePath(path)


def _IsFileRelativePath(path):
    return path.startswith("./") == 0 or path.startswith("../")


def _IsSearchPath(path):
    return _IsRelativePath(path) and not _IsFileRelativePath(path)


def _AnchorRelativePath(anchorPath, path):
    if (TfIsRelativePath(anchorPath) or not _IsRelativePath(path)):
        return path
    # Ensure we are using forward slashes and not back slashes.
    forwardPath = anchorPath.replace('\\', '/')
    # If anchorPath does not end with a '/', we assume it is specifying
    ## a file, strip off the last component, and anchor the path to that
    ## directory.
    anchoredPath = os.path.join(os.path.dirname(forwardPath), path)
    return os.path.normpath(anchoredPath)


def _ResolveAnchored(anchorPath, path):
    resolvedPath = path
    if (anchorPath):
        resolvedPath = os.path.join(anchorPath, path)
    return Ar.ResolvedPath(os.path.normpath(resolvedPath)) if os.path.isfile(resolvedPath) else Ar.ResolvedPath()


class Resolver:
    @staticmethod
    @log_function_args
    def _CreateIdentifier(assetPath, anchorAssetPath, serializedContext, serializedFallbackContext):
        """Returns an identifier for the asset specified by assetPath.
        If anchorAssetPath is not empty, it is the resolved asset path
        that assetPath should be anchored to if it is a relative path.
        Args:
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): An resolved anchor path.
        Returns:
            str: The identifier.
        """
        if not assetPath:
            return assetPath
        if not anchorAssetPath:
            return os.path.normpath(assetPath)
        anchoredAssetPath = _AnchorRelativePath(anchorAssetPath.GetPathString(), assetPath)
        if (_IsSearchPath(assetPath) and not Resolver._Resolve(anchorAssetPath.GetPathString(),serializedContext, serializedFallbackContext)):
            return os.path.normpath(assetPath)
        return os.path.normpath(anchoredAssetPath)

    @staticmethod
    @log_function_args
    def _CreateIdentifierForNewAsset(assetPath, anchorAssetPath):
        """Return an identifier for a new asset at the given assetPath.
        This is similar to _CreateIdentifier but is used to create identifiers
        for assets that may not exist yet and are being created.
        Args:
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): An resolved anchor path.
        Returns:
            str: The identifier.
        """
        if not assetPath:
            return assetPath
        if _IsRelativePath(assetPath):
            if anchorAssetPath:
                return os.path.normpath(_AnchorRelativePath(anchorAssetPath.GetPathString(), assetPath))
            else:
                return os.path.normpath(assetPath)
        return os.path.normpath(assetPath)

    @staticmethod
    @log_function_args
    def _Resolve(assetPath, contextSerialized, fallbackContextSerialized):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            Ar.ResolvedPath: The resolved path.
        """
        if not assetPath:
            return Ar.ResolvedPath()
        if _IsRelativePath(assetPath):
            if Resolver._IsContextDependentPath(assetPath):
                for ctx in [contextSerialized, fallbackContextSerialized]:
                    if not ctx:
                        continue
                    ctx = json.loads(ctx)
                    mappedPath = assetPath
                    if ctx.get(PythonResolver.Tokens.mappingRegexExpression, ""):
                        mappedPath = re.sub(ctx[PythonResolver.Tokens.mappingRegexExpression],
                                            ctx[PythonResolver.Tokens.mappingRegexFormat],
                                            mappedPath)
                    mappingPairs = ctx.get(PythonResolver.Tokens.mappingPairs, {})
                    mappedPath = mappingPairs.get(mappedPath, mappedPath)
                    for searchPath in ctx.get(PythonResolver.Tokens.searchPaths, []):
                        resolvedPath = _ResolveAnchored(searchPath, mappedPath)
                        if resolvedPath:
                            return resolvedPath
        return _ResolveAnchored("", assetPath)

    @staticmethod
    @log_function_args
    def _ResolveForNewAsset(assetPath):
        """Return the resolved path for the given assetPath that may be
        used to create a new asset or an empty ArResolvedPath if such a
        path cannot be computed.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            Ar.ResolvedPath: The resolved path.
        """
        return Ar.ResolvedPath(assetPath if not assetPath else os.path.normpath(assetPath))

    @staticmethod
    @log_function_args
    def _IsContextDependentPath(assetPath):
        """Returns true if assetPath is a context-dependent path, false otherwise.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            bool: The context-dependent state.
        """
        return _IsSearchPath(assetPath)

    @staticmethod
    @log_function_args
    def _GetModificationTimestamp(assetPath, resolvedPath):
        """Return an ArTimestamp representing the last time the asset at assetPath was modified.
        Args:
            assetPath (str): An unresolved asset path.
            resolvePath (Ar.ResolvedPath): A resolved path.
        Returns:
            Ar.Timestamp: The timestamp.
        """
        if not os.path.isfile(resolvedPath.GetPathString()):
            return Ar.Timestamp()
        return Ar.Timestamp(os.path.getmtime(resolvedPath.GetPathString()))

class ResolverContext:
    @staticmethod
    @log_function_args
    def LoadOrRefreshData(mappingFilePath):
        print(mappingFilePath)
        return "haha"