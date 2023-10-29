import inspect
import json
import logging
import re
import os
import sys
from functools import wraps

from pxr import Ar, Sdf
from usdAssetResolver.CachedResolver import Tokens

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



class Resolver:
    @staticmethod
    @log_function_args
    def ResolveAndCache(assetPath, context):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            Ar.ResolvedPath: The resolved path.
        """

        #raise Exception(">>>>>>>{}".format(dir(context)))
        print(":::::::::::::::::::::::::::::::::::::::::::::::::: Context ->", context.GetMappingPairs())
        context.AddMappingPair("debug", "How cool is this!")
        return Ar.ResolvedPath("Debug Working")

        # if not assetPath:
        #     return Ar.ResolvedPath()
        # if _IsRelativePath(assetPath):
        #     if Resolver._IsContextDependentPath(assetPath):
        #         for data in [serializedContext, serializedFallbackContext]:
        #             if not data:
        #                 continue
        #             try:
        #                 ctx = json.loads(data)
        #             except Exception:
        #                 print("Failed to extract context, data is not serialized json data: {data}".format(data=data))
        #                 continue
        #             mappingPairs = ctx.get(Tokens.mappingPairs, {})
        #             mappedPath = assetPath
        #             if mappingPairs:
        #                 if ctx.get(Tokens.mappingRegexExpression, ""):
        #                     mappedPath = re.sub(ctx[Tokens.mappingRegexExpression],
        #                                         ctx.get(Tokens.mappingRegexFormat, ""),
        #                                         mappedPath)
        #             mappedPath = mappingPairs.get(mappedPath, mappedPath)
        #             for searchPath in ctx.get(Tokens.searchPaths, []):
        #                 resolvedPath = _ResolveAnchored(searchPath, mappedPath)
        #                 if resolvedPath:
        #                     return resolvedPath
        # return _ResolveAnchored("", assetPath)
