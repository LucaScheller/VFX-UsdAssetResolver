import inspect
import logging
import os
import re
from functools import wraps

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)

# Globals
ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
SHOTS_DIR_PATH = os.path.join(ROOT_DIR_PATH, "workspace", "shots")
ASSETS_DIR_PATH = os.path.join(ROOT_DIR_PATH, "workspace", "assets")
ENTITY_TYPE_TO_DIR_PATH = {
    "shots": SHOTS_DIR_PATH,
    "assets": ASSETS_DIR_PATH
}
RELATIVE_PATH_IDENTIFIER_PREFIX = "relativeIdentifier|"
REGEX_VERSION = re.compile("(v\d\d\d)")

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
        # For this example, we assume all identifier are anchored to the shot and asset directories.
        # We remove the version from the identifier, so that our mapping files can target a version-less identifier.
        anchor_path = anchorAssetPath.GetPathString()
        anchor_path = anchor_path[:-1] if anchor_path[-1] == os.path.sep else anchor_path[:anchor_path.rfind(os.path.sep)]
        entity_type = os.path.basename(os.path.dirname(anchor_path))
        entity_identifier = os.path.basename(anchor_path)
        entity_element = os.path.basename(assetPath).split("_")[0]
        entity_version = REGEX_VERSION.search(os.path.basename(assetPath)).groups()[0]

        remapped_relative_path_identifier = f"{RELATIVE_PATH_IDENTIFIER_PREFIX}{entity_type}/{entity_identifier}?{entity_element}-{entity_version}"
        resolver.AddCachedRelativePathIdentifierPair(anchoredAssetPath, remapped_relative_path_identifier)

        # If you don't want this identifier to be passed through to ResolverContext.ResolveAndCache
        # or the mapping/caching mechanism, return this:
        # resolver.AddCachedRelativePathIdentifierPair(anchoredAssetPath, anchoredAssetPath)
        # return anchoredAssetPath

        return remapped_relative_path_identifier


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
        # context.AddCachingPair("assets/assetA", os.path.join(ASSETS_DIR_PATH, "assetA/assetA_v002.usd"))
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
        resolved_asset_path = ""
        if assetPath.startswith(RELATIVE_PATH_IDENTIFIER_PREFIX):
            base_identifier = assetPath[len(RELATIVE_PATH_IDENTIFIER_PREFIX):]
            anchor_path, entity_element = base_identifier.split("?")
            entity_type, entity_identifier = anchor_path.split("/")
            entity_element, entity_version = entity_element.split("_")
            # Here you would add your custom relative path resolve logic.
            # We can test our mapping pairs to see if the version is pinned, otherwise we fallback to the original intent.
            versionless_identifier = f"{RELATIVE_PATH_IDENTIFIER_PREFIX}{entity_type}/{entity_identifier}?{entity_element}"
            mapping_pairs = context.GetMappingPairs()
            mapping_hit = mapping_pairs.get(versionless_identifier)
            if mapping_hit:
                resolved_asset_path = mapping_hit
            else:
                resolved_asset_path = os.path.normpath(os.path.join(ENTITY_TYPE_TO_DIR_PATH[entity_type],
                                                                    entity_identifier,
                                                                    "elements", f"{entity_element}_{entity_version}.usd"))
        else:
            entity_type, entity_identifier = assetPath.split("/")
            # Here you would add your custom "latest version" query.
            resolved_asset_path = os.path.join(ENTITY_TYPE_TO_DIR_PATH[entity_type],
                                                entity_identifier,
                                                f"{entity_identifier}_v002.usd")
        # Cache result
        context.AddCachingPair(assetPath, resolved_asset_path)
        return resolved_asset_path