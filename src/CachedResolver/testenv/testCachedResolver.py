from __future__ import print_function
import tempfile
import os

from pxr import Ar, Sdf, Usd, Vt
from usdAssetResolver import CachedResolver

import unittest


class TestArResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force Ar to use our CachedResolver implementation.
        Ar.SetPreferredResolver("CachedResolver")
        # Verify that the underlying resolver is the CachedResolver
        assert isinstance(Ar.GetUnderlyingResolver(), CachedResolver.Resolver)

    def test_debug(self):
        resolver = Ar.GetResolver()
        resolved_path = resolver.Resolve("debug")
        print("::::::::::::::::::::::::::::::::::::::: Result Call 1 ->", resolved_path)
        resolved_path = resolver.Resolve("debug")
        print("::::::::::::::::::::::::::::::::::::::: Result Call 2 ->", resolved_path)

    def _test_CreateIdentifier(self):
        resolver = Ar.GetResolver()

        # Test for invalid paths
        self.assertEqual("", resolver.CreateIdentifier(""))
        self.assertEqual(
            "", resolver.CreateIdentifier("", Ar.ResolvedPath("some/relative/path.usd"))
        )
        self.assertEqual(
            "",
            resolver.CreateIdentifier("", Ar.ResolvedPath("/some/absolute/path.usd")),
        )

        # Test for valid paths
        self.assertEqual(
            "/some/absolute/path.usd",
            resolver.CreateIdentifier(
                "/some/absolute/path.usd", Ar.ResolvedPath("some/relative/path.usd")
            ),
        )
        self.assertEqual(
            "/some/absolute/path.usd",
            resolver.CreateIdentifier(
                "/some/absolute/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )

        self.assertEqual(
            "/some/absolute/some/relative/path.usd",
            resolver.CreateIdentifier(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/absolute/")
            ),
        )
        self.assertEqual(
            "/some/absolute/some/relative/path.usd",
            resolver.CreateIdentifier(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )
        self.assertEqual(
            "/some/some/relative/path.usd",
            resolver.CreateIdentifier(
                "../some/relative/path.usd", Ar.ResolvedPath("/some/absolute/")
            ),
        )
        self.assertEqual(
            "/some/some/relative/path.usd",
            resolver.CreateIdentifier(
                "../some/relative/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )

        self.assertEqual(
            "/other/relative/path.usd",
            resolver.CreateIdentifier(
                "/some/../other/relative/path.usd",
                Ar.ResolvedPath("/some/absolute/path.usd"),
            ),
        )

    def _test_CreateIdentifierForNewAsset(self):
        resolver = Ar.GetResolver()

        # Test for invalid paths
        self.assertEqual("", resolver.CreateIdentifierForNewAsset(""))
        self.assertEqual(
            "",
            resolver.CreateIdentifierForNewAsset(
                "", Ar.ResolvedPath("some/relative/path.usd")
            ),
        )
        self.assertEqual(
            "",
            resolver.CreateIdentifierForNewAsset(
                "", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )

        # Test for valid paths
        self.assertEqual(
            "/some/absolute/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "/some/absolute/path.usd", Ar.ResolvedPath("some/relative/path.usd")
            ),
        )
        self.assertEqual(
            "/some/absolute/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "/some/absolute/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )

        self.assertEqual(
            "/some/absolute/some/relative/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/absolute/")
            ),
        )
        self.assertEqual(
            "/some/absolute/some/relative/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )
        self.assertEqual(
            "/some/some/relative/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "../some/relative/path.usd", Ar.ResolvedPath("/some/absolute/")
            ),
        )
        self.assertEqual(
            "/some/some/relative/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "../some/relative/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )

        self.assertEqual(
            "/other/relative/path.usd",
            resolver.CreateIdentifierForNewAsset(
                "/some/../other/relative/path.usd",
                Ar.ResolvedPath("/some/absolute/path.usd"),
            ),
        )

    def _test_Resolve(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.SetCustomSearchPaths([temp_dir_path])
            ctx.RefreshSearchPaths()
            # Create files
            layer_identifier = "layer.usd"
            layer_file_path = os.path.join(temp_dir_path, layer_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_file_path)
            # Get resolver
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                resolved_path = resolver.Resolve(layer_identifier)
                self.assertEqual(resolved_path.GetPathString(), layer_file_path)
                self.assertTrue(os.path.isabs(resolved_path.GetPathString()))
                resolved_path = resolver.Resolve("example.usd")
                self.assertEqual(resolved_path.GetPathString(), "")
                resolved_path = resolver.Resolve("/some/invalid/path.usd")
                self.assertEqual(resolved_path.GetPathString(), "")
                resolved_path = resolver.Resolve(layer_file_path)
                self.assertEqual(resolved_path.GetPathString(), layer_file_path)

    def _test_ResolveForNewAsset(self):
        resolver = Ar.GetResolver()

        layer_identifier = "layer.usd"
        layer_file_path = os.path.join(os.getcwd(), layer_identifier)
        resolved_path = resolver.ResolveForNewAsset(layer_identifier)
        self.assertEqual(resolved_path.GetPathString(), layer_file_path)

        layer_identifier = "../layer.usd"
        layer_file_path = os.path.abspath(os.path.join(os.getcwd(), layer_identifier))
        resolved_path = resolver.ResolveForNewAsset(layer_identifier)
        self.assertEqual(resolved_path.GetPathString(), layer_file_path)

    def _test_ResolveWithCache(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.SetCustomSearchPaths([temp_dir_path])
            ctx.RefreshSearchPaths()
            # Create files
            layer_identifier = "layer.usd"
            layer_file_path = os.path.join(temp_dir_path, layer_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_file_path)
            # Get resolver
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                with Ar.ResolverScopedCache():
                    # Resolve
                    self.assertEqual(
                        os.path.abspath(layer_file_path),
                        resolver.Resolve(layer_identifier),
                    )
                    # Remove file
                    os.remove(layer_file_path)
                    # Query cached result
                    self.assertEqual(
                        os.path.abspath(layer_file_path),
                        resolver.Resolve(layer_identifier),
                    )
                # Uncached result should now return empty result
                self.assertEqual("", resolver.Resolve(layer_identifier))

    def _test_ResolveWithContext(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.SetCustomSearchPaths([temp_dir_path])
            ctx.RefreshSearchPaths()
            ctx.SetMappingRegexExpression("(v\d\d\d)")
            ctx.SetMappingRegexFormat("v000")
            ctx.AddMappingPair("layer_v000.usd", "layer_v002.usd")
            # Create files
            layer_v001_identifier = "layer_v001.usd"
            layer_v001_file_path = os.path.join(temp_dir_path, layer_v001_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_v001_file_path)
            layer_v002_identifier = "layer_v002.usd"
            layer_v002_file_path = os.path.join(temp_dir_path, layer_v002_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_v002_file_path)
            # Get resolver
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                resolved_path = resolver.Resolve(layer_v001_identifier)
                self.assertEqual(resolved_path.GetPathString(), layer_v002_file_path)

    def _test_ResolveWithCacheContextRefresh(self):
        """This test currently does not work.
        # ToDo Investigate why RefreshContext doesn't flush ResolverScopedCaches
        """
        if True:
            return
        with tempfile.TemporaryDirectory() as temp_dir_path:
            stage = Usd.Stage.CreateInMemory()
            ctx_collection = stage.GetPathResolverContext()
            ctx = ctx_collection.Get()[0]
            ctx.SetCustomSearchPaths([temp_dir_path])
            ctx.RefreshSearchPaths()
            # Create files
            layer_a_identifier = "layerA.usd"
            layer_a_file_path = os.path.join(temp_dir_path, layer_a_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_a_file_path)
            layer_b_identifier = "layerB.usd"
            layer_b_file_path = os.path.join(temp_dir_path, layer_b_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_b_file_path)
            # Get resolver
            with Ar.ResolverScopedCache():
                # Resolve
                self.assertEqual(
                    os.path.abspath(layer_a_file_path),
                    stage.ResolveIdentifierToEditTarget(layer_a_identifier),
                )
                # Make edits to context
                ctx.AddMappingPair(layer_a_identifier, layer_b_identifier)
                resolver = Ar.GetResolver()
                resolver.RefreshContext(ctx)
                # Query cached result
                self.assertEqual(
                    os.path.abspath(layer_b_file_path),
                    stage.ResolveIdentifierToEditTarget(layer_a_identifier),
                )

    def _test_ResolverContextSearchPaths(self):
        ctx = CachedResolver.ResolverContext()
        # The default env search paths are passed in through cmake test env vars
        self.assertEqual(
            ctx.GetSearchPaths(), ["/env/search/pathA", "/env/search/pathB"]
        )
        self.assertEqual(
            ctx.GetEnvSearchPaths(), ["/env/search/pathA", "/env/search/pathB"]
        )
        self.assertEqual(ctx.GetCustomSearchPaths(), [])
        # Test env search paths
        os.environ["AR_SEARCH_PATHS"] = "/env/search/pathC:/env/search/pathD"
        self.assertEqual(
            ctx.GetEnvSearchPaths(), ["/env/search/pathA", "/env/search/pathB"]
        )
        ctx.RefreshSearchPaths()
        self.assertEqual(
            ctx.GetEnvSearchPaths(), ["/env/search/pathC", "/env/search/pathD"]
        )
        # Test custom search paths
        ctx.SetCustomSearchPaths(["/custom/search/pathA", "/custom/search/pathB"])
        self.assertEqual(
            ctx.GetSearchPaths(), ["/env/search/pathC", "/env/search/pathD"]
        )
        ctx.RefreshSearchPaths()
        self.assertEqual(
            ctx.GetSearchPaths(),
            [
                "/env/search/pathC",
                "/env/search/pathD",
                "/custom/search/pathA",
                "/custom/search/pathB",
            ],
        )
        # Test context (re-)creation
        os.environ["AR_SEARCH_PATHS"] = "/env/search/pathA:/env/search/pathB"
        ctx = CachedResolver.ResolverContext()
        # Previous context editing should have no influence
        self.assertEqual(
            ctx.GetSearchPaths(), ["/env/search/pathA", "/env/search/pathB"]
        )

    def _test_ResolverContextHash(self):
        self.assertEqual(
            hash(CachedResolver.ResolverContext()), hash(CachedResolver.ResolverContext())
        )
        # Currently only the pinning file path influences the hash
        search_paths = ["/custom/search/pathA", "/custom/search/pathB"]
        self.assertEqual(
            hash(CachedResolver.ResolverContext(search_paths)),
            hash(CachedResolver.ResolverContext()),
        )
        self.assertNotEqual(
            hash(CachedResolver.ResolverContext("/some/mapping/file.usd")),
            hash(CachedResolver.ResolverContext()),
        )

    def _test_ResolverContextRepr(self):
        self.assertEqual(
            repr(CachedResolver.ResolverContext("/some/mapping/file.usd")),
            "CachedResolver.ResolverContext('/some/mapping/file.usd')",
        )

    def _test_ResolverContextMappingPairs(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create mapping file
            mapping_file_path = os.path.join(temp_dir_path, "mapping.usd")

            mapping_layer = Sdf.Layer.CreateAnonymous()
            mapping_pairs = {
                "assets/assetA/assetA.usd": "assets/assetA/assetA_v005.usd",
                "shots/shotA/shotA_v000.usd": "shots/shotA/shotA_v003.usd",
            }
            mapping_array = []
            for source_path, target_path in mapping_pairs.items():
                mapping_array.extend([source_path, target_path])
            mapping_layer.customLayerData = {
                CachedResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)
            }
            mapping_layer.Export(mapping_file_path)

            # Test mapping file load
            ctx = CachedResolver.ResolverContext(mapping_file_path)
            self.assertEqual(ctx.GetMappingFilePath(), mapping_file_path)
            self.assertEqual(ctx.GetMappingPairs(), mapping_pairs)
            # Test mapping add
            mapping_pairs_updated = {k: v for k, v in ctx.GetMappingPairs().items()}
            ctx.AddMappingPair("example/cube", "example/sphere")
            ctx.AddMappingPair("example/cone", "example/triangle")
            ctx.AddMappingPair("example/cylinder", "example/sphere")
            self.assertNotEqual(ctx.GetMappingPairs(), mapping_pairs_updated)
            mapping_pairs_updated["example/cube"] = "example/sphere"
            mapping_pairs_updated["example/cone"] = "example/triangle"
            mapping_pairs_updated["example/cylinder"] = "example/sphere"
            self.assertEqual(ctx.GetMappingPairs(), mapping_pairs_updated)
            # Test mapping remove
            ctx.RemoveMappingByKey("example/cone")
            self.assertNotEqual(ctx.GetMappingPairs(), mapping_pairs_updated)
            mapping_pairs_updated.pop("example/cone")
            self.assertEqual(ctx.GetMappingPairs(), mapping_pairs_updated)

            ctx.RemoveMappingByValue("example/sphere")
            self.assertNotEqual(ctx.GetMappingPairs(), mapping_pairs_updated)
            mapping_pairs_updated.pop("example/cube")
            mapping_pairs_updated.pop("example/cylinder")
            self.assertEqual(ctx.GetMappingPairs(), mapping_pairs_updated)
            # Test clear
            ctx.ClearMappingPairs()
            self.assertEqual(ctx.GetMappingPairs(), {})
            # Test refresh from file
            ctx.RefreshFromMappingFilePath()
            self.assertEqual(ctx.GetMappingPairs(), mapping_pairs)

    def _test_ResolverContextRegexExpressions(self):
        ctx = CachedResolver.ResolverContext()
        # The default regex expression values are passed in through cmake test env vars
        self.assertEqual(ctx.GetMappingRegexExpression(), "(v\d\d\d)")
        self.assertEqual(ctx.GetMappingRegexFormat(), "v000")
        ctx.SetMappingRegexExpression("(cube)")
        ctx.SetMappingRegexFormat("Cube")
        self.assertEqual(ctx.GetMappingRegexExpression(), "(cube)")
        self.assertEqual(ctx.GetMappingRegexFormat(), "Cube")


if __name__ == "__main__":
    unittest.main()
