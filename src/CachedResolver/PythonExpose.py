import inspect
import logging
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


class ResolverContext:
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
        resolved_asset_path = assetPath
        context.AddCachePair(assetPath, resolved_asset_path)
        LOG.debug("::: ResolveAndCache | {}".format(context.GetCachingPairs()))
        """
        To clear the context cache call:
        context.ClearCachingPairs()
        """
        return Ar.ResolvedPath(resolved_asset_path)
