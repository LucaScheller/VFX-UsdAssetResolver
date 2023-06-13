import inspect
import logging
from functools import wraps

from pxr import Ar

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)

# Utils
def log_function_args(func):
    """Decorator to print function call details."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        LOG.info(f"{func.__module__}.{func.__qualname__} ({func_args_str})")
        return func(*args, **kwargs)

    return wrapper

class Resolver:
    @staticmethod
    @log_function_args
    def _CreateIdentifier(assetPath, anchorAssetPath):
        """Returns an identifier for the asset specified by assetPath.
        If anchorAssetPath is not empty, it is the resolved asset path
        that assetPath should be anchored to if it is a relative path.
        Args:
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): An resolved anchor path.
        Returns:
            str: The identifier.
        """
        return assetPath

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
        return assetPath

    @staticmethod
    @log_function_args
    def _Resolve(assetPath):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            Ar.ResolvedPath: The resolved path.
        """
        print(">>>>>>>>>>>>>>>>>>>>", assetPath)
        return Ar.ResolvedPath(assetPath)

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
        return Ar.ResolvedPath(assetPath)

    @staticmethod
    @log_function_args
    def _CreateDefaultContext():
        pass

    @staticmethod
    @log_function_args
    def _CreateDefaultContextForAsset(assetPath):
        pass

    @staticmethod
    @log_function_args
    def _IsContextDependentPath(assetPath):
        """Returns true if assetPath is a context-dependent path, false otherwise.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            bool: The context-dependent state.
        """
        return False

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
        return Ar.Timestamp(0)

class ResolverContext:
    @staticmethod
    @log_function_args
    def test():
        pass