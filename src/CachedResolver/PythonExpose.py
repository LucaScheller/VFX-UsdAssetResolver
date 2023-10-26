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
SYSTEM_IS_WINDOWS = sys.platform.lower() == "windows"

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
        return _ResolveAnchored("", assetPath)

    @staticmethod
    @log_function_args
    def _IsContextDependentPath(assetPath):
        """Returns true if assetPath is a context-dependent path, false otherwise.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            bool: The context-dependent state.
        """
        # ToDo This is not used, please see the _IsContextDependentPath (docstring)
        # for more information. This can't be implmented in Python due to it 
        # being performance critical function.
        raise NotImplementedError

class ResolverContext:
    @staticmethod
    @log_function_args
    def LoadOrRefreshData(mappingFilePath, searchPathsEnv, mappingRegexExpressionEnv, mappingRegexFormatEnv):
        """Load or refresh the mapping pairs from file and the search paths from the
        configured environment variables.
        Args:
            mappingFilePath(str): The mapping .usd file path
            searchPathsEnv(str): The search paths environment variable
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