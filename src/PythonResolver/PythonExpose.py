import inspect
import json
import logging
import re
import os
import sys
from functools import wraps

from pxr import Ar, Sdf
from usdAssetResolver.PythonResolver import Tokens

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)

# Utils
SYSTEM_IS_LINUX = sys.platform.lower() == "linux"
SYSTEM_IS_WINDOWS = any([w in sys.platform.lower() for w in ["windows", "win32", "win64", "cygwin"]])

def log_function_args(func):
    """Decorator to print function call details."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        # To enable logging on all methods, re-enable this.
        # LOG.info(f"{func.__module__}.{func.__qualname__} ({func_args_str})")
        return func(*args, **kwargs)

    return wrapper


def TfIsRelativePath(path):
    """Check if the path is not an absolute path,
    by checking if it starts with "/" or "\\" depending on the host
    os path style.
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a relative path
    """
    if SYSTEM_IS_WINDOWS:
        drive, tail = os.path.splitdrive(path)
        return not path or (path[0] != '/' and path[0] != '\\' and not drive)
    else:
        return not path or path[0] != '/'


def _IsRelativePath(path):
    """Check if the path is not an absolute path,
    by checking if it starts with "/" or "\\"
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a relative path
    """
    return path and TfIsRelativePath(path)


def _IsFileRelativePath(path):
    """Check if the path is a relative file path
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a relative file path
    """
    return path.startswith("./") or path.startswith("../")


def _IsSearchPath(path):
    """Check if the path is search path resolveable
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a search path resolveable path
    """
    return _IsRelativePath(path) and not _IsFileRelativePath(path)


def _AnchorRelativePath(anchorPath, path):
    """Anchor the relative path by the anchor path.
    Args:
        anchorPath(str): The anchor path
        path(str): The path to anchor
    Returns:
        str: An anchored path
    """
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
    """Anchor the path by the anchor path.
    Args:
        anchorPath(str): The anchor path
        path(str): The path to anchor
    Returns:
        Ar.ResolvedPath: An anchored resolved path
    """
    resolvedPath = path
    if (anchorPath):
        resolvedPath = os.path.join(anchorPath, path)
    return Ar.ResolvedPath(os.path.normpath(resolvedPath)) if os.path.isfile(resolvedPath) else Ar.ResolvedPath()


def _GetMappingPairsFromUsdFile(mappingFilePath):
    """Lookup mapping pairs from the given mapping .usd file.
    Args:
        mappingFilePath(str): The mapping .usd file path
    Returns:
        mappingPairs(dict): A dict of mapping pairs
    """
    if not os.path.isfile(mappingFilePath) or not mappingFilePath.endswith((".usd", ".usdc", ".usda")):
        return {}
    layer = Sdf.Layer.FindOrOpen(mappingFilePath)
    if not layer:
        return {}
    layerMetaData = layer.customLayerData
    mappingPairs = layerMetaData.get(Tokens.mappingPairs)
    if not mappingPairs:
        return {}
    if len(mappingPairs) % 2 != 0:
        return {}
    mappingPairs = dict(zip(mappingPairs[::2], mappingPairs[1::2]))
    return mappingPairs


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
            serializedContext (str): The serialized context.
            serializedFallbackContext (str): The serialized fallback context.
        Returns:
            str: The identifier.
        """
        if not assetPath:
            return assetPath
        if not anchorAssetPath:
            return os.path.normpath(assetPath)
        anchoredAssetPath = _AnchorRelativePath(anchorAssetPath.GetPathString(), assetPath)
        if (_IsSearchPath(assetPath) and not Resolver._Resolve(anchoredAssetPath,serializedContext, serializedFallbackContext)):
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
    def _Resolve(assetPath, serializedContext, serializedFallbackContext):
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
                for data in [serializedContext, serializedFallbackContext]:
                    if not data:
                        continue
                    try:
                        ctx = json.loads(data)
                    except Exception:
                        print("Failed to extract context, data is not serialized json data: {data}".format(data=data))
                        continue
                    mappingPairs = ctx.get(Tokens.mappingPairs, {})
                    mappedPath = assetPath
                    if mappingPairs:
                        if ctx.get(Tokens.mappingRegexExpression, ""):
                            mappedPath = re.sub(ctx[Tokens.mappingRegexExpression],
                                                ctx.get(Tokens.mappingRegexFormat, ""),
                                                mappedPath)
                    mappedPath = mappingPairs.get(mappedPath, mappedPath)
                    for searchPath in ctx.get(Tokens.searchPaths, []):
                        resolvedPath = _ResolveAnchored(searchPath, mappedPath)
                        if resolvedPath:
                            return resolvedPath
                    # Only try the first valid context.
                    break
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
        return Ar.ResolvedPath(assetPath if not assetPath else os.path.abspath(os.path.normpath(assetPath)))

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
    def LoadOrRefreshData(mappingFilePath, searchPathsEnv, mappingRegexExpressionEnv, mappingRegexFormatEnv):
        """Load or refresh the mapping pairs from file and the search paths from the
        configured environment variables.
        Args:
            mappingFilePath(str): The mapping .usd file path
            searchPathsEnv(str): The search paths environment variable
            mappingRegexExpressionEnv(str): The mapping regex expression environment variable
            mappingRegexFormatEnv(str): The mapping regex format environment variable
        Returns:
            str: A serialized json dict that can be used as a context.
        """
        ctx = {}
        # Search Paths
        searchPaths = os.environ.get(searchPathsEnv, "").split(os.path.pathsep)
        searchPaths = [os.path.normpath(path) for path in searchPaths]
        ctx[Tokens.searchPaths] = searchPaths
        # Regex Formatting
        ctx[Tokens.mappingRegexExpression] = os.environ.get(mappingRegexExpressionEnv, "")
        ctx[Tokens.mappingRegexFormat] = os.environ.get(mappingRegexFormatEnv, "")
        # Mapping Pairs
        mappingPairs = _GetMappingPairsFromUsdFile(mappingFilePath)
        ctx[Tokens.mappingPairs] = mappingPairs
        return json.dumps(ctx)