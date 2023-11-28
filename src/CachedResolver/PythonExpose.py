# pylint: disable=invalid-name
import os
import logging
import json


from pxr import Ar  # pylint: disable=unused-import

# This import is needed so that our methods below know what a CachedResolver.Context is!
from usdAssetResolver import CachedResolver  # pylint: disable=unused-import

from rdo_publish_pipeline import manager

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)


class ResolverContext:

    RDOJSON_PREFIX = "rdojson:"
    ENABLE_ENV_VAR = "RDO_USD_CACHED_RESOLVER_ENABLE_SHOTGRID"

    @staticmethod
    def Initialize(context):  # pylint: disable=unused-argument
        """Initialize the context. This get's called on default and post mapping file path
        context creation.

        Here you can inject data by batch calling context.AddCachingPair(assetPath, resolvePath),
        this will then populate the internal C++ resolve cache and all resolves calls
        to those assetPaths will not invoke Python and instead use the cache.

        Args:
            context (CachedResolverContext): The active context.
        """
        LOG.debug("CachedResolver.PythonExport.ResolverContext.Initialize")

    @staticmethod
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
        LOG.debug("CachedResolver.PythonExport.ResolverContext.ResolveAndCache %s", assetPath)

        # This should not really happen because we set the uriScheme in the plugInfo.json config
        if not assetPath.startswith(ResolverContext.RDOJSON_PREFIX):
            LOG.error(
                "Asset path is not using valid URI (%s) %s",
                ResolverContext.RDOJSON_PREFIX,
                assetPath,
            )
            return ""

        if os.environ.get(ResolverContext.ENABLE_ENV_VAR) != "1":
            LOG.warning(
                "ShotGrid query is not enabled. export %s=1",
                ResolverContext.ENABLE_ENV_VAR,
            )
            return ""

        resolvedAssetPath = ResolverContext._getPublishedFilePathFromJsonAsset(assetPath)
        if not resolvedAssetPath:
            return ""

        context.AddCachingPair(assetPath, resolvedAssetPath)

        return resolvedAssetPath

    @staticmethod
    def _getPublishedFilePathFromJsonAsset(assetPath):
        """Decode json asset path and use dict content to query published file.

        Args:
            assetPath (str): An unresolved asset path.

        Returns:
            str: The resolved path string.
        """
        jsonStr = assetPath[len(ResolverContext.RDOJSON_PREFIX) :]
        try:
            json_data = json.loads(jsonStr)
        except ValueError:
            LOG.error("Invalid JSON: %s", jsonStr)
            return

        publishStr = json_data.get("publish", "")
        try:
            publish = manager.Publish.fromString(publishStr)
        except ValueError:
            LOG.error("Invalid publish: %s", publishStr)
            return

        version = json_data.get("version", "latestApprovedOrLatest")
        if not isinstance(version, int):
            try:
                version = getattr(manager.version, version)
            except AttributeError:
                LOG.error("Invalid version string: %s", version)
                return

        published_file = publish.version(version)
        if not published_file:
            LOG.error("No published file for version: %s", version)
            return

        try:
            subdir = json_data.get("subdir", "")
            if subdir:
                return published_file.path.asDict().get(subdir, [])[0]
            return published_file.path[0]
        except IndexError:
            LOG.error("Unable to get published file path for asset: %s", assetPath)
