import inspect
import logging
import os
from functools import wraps

from pxr import Ar
# This import is needed so that our methods below know what a CachedResolver.Context is!
from usdAssetResolver import CachedResolver

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)


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


class UnitTestHelper:
    context_initialize_call_counter = 0
    resolve_and_cache_call_counter = 0
    current_directory_path = ""

    @classmethod
    def reset(cls, current_directory_path=""):
        cls.context_initialize_call_counter = 0
        cls.resolve_and_cache_call_counter = 0
        cls.current_directory_path = current_directory_path


class ResolverContext:

    @staticmethod
    @log_function_args
    def Initialize(context):
        """Initialize the context. This get's called on default and post mapping file path
        context creation.

        Here you can inject data by batch calling context.AddCachingPair(assetPath, resolvePath),
        this will then populate the internal C++ resolve cache and all resolves calls
        to those assetPaths will not invoke Python and instead use the cache.

        Args:
            context (CachedResolverContext): The active context.
        """
        LOG.debug("::: ResolverContext.Initialize")
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.context_initialize_call_counter += 1
        context.AddCachingPair("shot.usd", "/some/path/to/a/file.usd")
        return

    @staticmethod
    @log_function_args
    def ResolveAndCache(assetPath, context):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            assetPath (str): An unresolved asset path.
            context (CachedResolverContext): The active context.
        Returns:
            str: The resolved path string. If it points to a non-existent file,
                 it will be resolved to an empty ArResolvedPath internally, but will
                 still count as a cache hit and be stored inside the cachedPairs dict.
        """
        resolved_asset_path = "/some/path/to/a/file.usd"
        context.AddCachingPair(assetPath, resolved_asset_path)
        LOG.debug(
            "::: ResolverContext.ResolveAndCache | {} | {}".format(assetPath, context.GetCachingPairs())
        )
        """
        To clear the context cache call:
        context.ClearCachingPairs()
        """
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.resolve_and_cache_call_counter += 1
        if assetPath == "unittest.usd":
            current_dir_path = UnitTestHelper.current_directory_path
            asset_a_file_path = os.path.join(current_dir_path, "assetA.usd")
            asset_b_file_path = os.path.join(current_dir_path, "assetB.usd")
            context.AddCachingPair("assetA.usd", asset_a_file_path)
            context.AddCachingPair("assetB.usd", asset_b_file_path)
        return resolved_asset_path
