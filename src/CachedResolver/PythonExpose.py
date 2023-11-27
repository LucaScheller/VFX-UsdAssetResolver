import inspect
import logging
import os
import json
from functools import wraps

import six

from pxr import Ar  # pylint: disable=unused-import
# This import is needed so that our methods below know what a CachedResolver.Context is!
from usdAssetResolver import CachedResolver  # pylint: disable=unused-import

from rdo_publish_pipeline import manager

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)


def log_function_args(func):
    """Decorator to print function call details."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # To enable logging on all methods, re-enable this.
        # if six.PY2:
        #     # no inspect.signature in py2
        #     func_args_str = ", ".join([str(arg) for arg in args])
        #     func_kwargs_str = ", ".join(map("{0[0]} = {0[1]!r}".format, kwargs.items()))
        #     LOG.info("%s.%s (%s, %s)", func.__module__, func.__name__, func_args_str, func_kwargs_str)
        # else:
        #     func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        #     func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        #     LOG.info("%s.%s (%s)", func.__module__, func.__qualname__, func_args_str)
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
    
    RDOJSON_PREFIX = "rdojson:"
    
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
#         context.AddCachingPair("shot.usd", "/some/path/to/a/file.usd")
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
        
        resolved_asset_path = ""
        if assetPath.startswith(ResolverContext.RDOJSON_PREFIX):
            try:
                resolved_asset_path = ResolverContext._getPublishedFilePathFromJsonAsset(assetPath) or ""
            except Exception as err:
                LOG.error(str(err))

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

    @staticmethod
    @log_function_args
    def _getPublishedFilePathFromJsonAsset(assetPath):
        """Decode json asset path and use dict content to query published file.

        Args:
            assetPath (str): An unresolved asset path.

        Returns:
            str: The resolved path string.
        """
        json_str = assetPath[len(ResolverContext.RDOJSON_PREFIX):]
        try:
            json_data = json.loads(json_str)
        except ValueError:
            LOG.error("Invalid JSON: %s", json_str)
            return
        
        publish_str = json_data.get("publish", "")
        try:
            publish = manager.Publish.fromString(publish_str)
        except ValueError:
            LOG.error("Invalid publish: %s", publish_str)
            return
        
        if publish:
                
            version = json_data.get("version", "latestApprovedOrLatest")
            if not isinstance(version, int):
                try:
                    version = getattr(manager.version, version)
                except AttributeError:
                    LOG.error("Invalid version string: %s", version)
                    return
            
            published_file = publish.version(version)
            if published_file:
                subdir = json_data.get("subdir")
                if subdir:
                    return published_file.path.asDict().get(subdir)[0]            
                return published_file.path[0]
        
