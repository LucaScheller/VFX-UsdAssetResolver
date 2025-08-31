import inspect
import logging
import os
from functools import wraps

from pxr import Ar


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
    create_relative_path_identifier_call_counter = 0
    context_initialize_call_counter = 0
    resolve_and_cache_call_counter = 0
    current_directory_path = ""

    @classmethod
    def reset(cls, current_directory_path=""):
        cls.create_relative_path_identifier_call_counter = 0
        cls.context_initialize_call_counter = 0
        cls.resolve_and_cache_call_counter = 0
        cls.current_directory_path = current_directory_path


class Resolver:

    @staticmethod
    @log_function_args
    def CreateRelativePathIdentifier(resolver, anchoredAssetPath, assetPath, anchorAssetPath):
        """Returns an identifier for the asset specified by assetPath and anchor asset path.
        It is very important that the anchoredAssetPath is used as the cache key, as this
        is what is used in C++ to do the cache lookup.

        We have two options how to return relative identifiers:
        - Make it absolute: Simply return the anchoredAssetPath. This means the relative identifier
                            will not be passed through to ResolverContext.ResolveAndCache.
        - Make it non file based: Make sure the remapped identifier does not start with "/", "./" or"../"
                                  by putting some sort of prefix in front of it. The path will then be
                                  passed through to ResolverContext.ResolveAndCache, where you need to re-construct
                                  it to an absolute path of your liking. Make sure you don't use a "<somePrefix>:" syntax,
                                  to avoid mixups with URI based resolvers.

        Args:
            resolver (CachedResolver): The resolver
            anchoredAssetPath (str): The anchored asset path, this has to be used as the cached key.
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): A resolved anchor path.

        Returns:
            str: The identifier.
        """
        LOG.debug("::: Resolver.CreateRelativePathIdentifier | {} | {} | {}".format(anchoredAssetPath, assetPath, anchorAssetPath))
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.create_relative_path_identifier_call_counter += 1
        remappedRelativePathIdentifier = f"relativePath|{assetPath}?{anchorAssetPath}".replace("\\", "/")
        resolver.AddCachedRelativePathIdentifierPair(anchoredAssetPath, remappedRelativePathIdentifier)
        return remappedRelativePathIdentifier


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
    def ResolveAndCache(context, assetPath):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            context (CachedResolverContext): The active context.
            assetPath (str): An unresolved asset path.
        Returns:
            str: The resolved path string. If it points to a non-existent file,
                 it will be resolved to an empty ArResolvedPath internally, but will
                 still count as a cache hit and be stored inside the cachedPairs dict.
        """
        LOG.debug(
            "::: ResolverContext.ResolveAndCache | {} | {}".format(assetPath, context.GetCachingPairs())
        )
        """Implement custom resolve logic and add the resolved path to the cache.
        resolved_asset_path = "/some/path/to/a/file.usd"
        context.AddCachingPair(assetPath, resolved_asset_path)
        # To clear the context cache call:
        context.ClearCachingPairs()
        """
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.resolve_and_cache_call_counter += 1
        resolved_asset_path = "/some/path/to/a/file.usd"
        context.AddCachingPair(assetPath, resolved_asset_path)
        if assetPath == "unittest.usd":
            current_dir_path = UnitTestHelper.current_directory_path
            asset_a_file_path = os.path.join(current_dir_path, "assetA.usd")
            asset_b_file_path = os.path.join(current_dir_path, "assetB.usd")
            context.AddCachingPair("assetA.usd", asset_a_file_path)
            context.AddCachingPair("assetB.usd", asset_b_file_path)
        relative_path_prefix = "relativePath|"
        if assetPath.startswith(relative_path_prefix):
            relative_path, anchor_path = assetPath[len(relative_path_prefix) :].split(
                "?"
            )
            anchor_path = anchor_path[:-1] if anchor_path[-1] == os.path.sep else anchor_path[:anchor_path.rfind(os.path.sep)]
            resolved_asset_path = os.path.normpath(os.path.join(anchor_path, relative_path))
            context.AddCachingPair(assetPath, resolved_asset_path)
        return resolved_asset_path
