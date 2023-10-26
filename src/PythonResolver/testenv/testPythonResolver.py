from __future__ import print_function
import json
import tempfile
import os

from pxr import Ar, Sdf, Usd, Vt
from usdAssetResolver import PythonResolver

import unittest


class TestArResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force Ar to use our PythonResolver implementation.
        Ar.SetPreferredResolver("PythonResolver")
        # Verify that the underlying resolver is the PythonResolver
        assert isinstance(Ar.GetUnderlyingResolver(), PythonResolver.Resolver)

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
            ctx = PythonResolver.ResolverContext()
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
            ctx = PythonResolver.ResolverContext()
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

    def test_ResolveWithContext(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create context
            ctx = PythonResolver.ResolverContext()
            ctx_data = json.loads(ctx.GetData())
            ctx_data[PythonResolver.Tokens.searchPaths] = [temp_dir_path]
            ctx_data[PythonResolver.Tokens.mappingRegexExpression] = "(v\d\d\d)"
            ctx_data[PythonResolver.Tokens.mappingRegexFormat] = "v000"
            ctx_data[PythonResolver.Tokens.mappingPairs] = {"layer_v000.usd": "layer_v002.usd"}
            ctx.SetData(json.dumps(ctx_data))
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

    def test_ResolverContextSearchPaths(self):
        ctx = PythonResolver.ResolverContext()
        ctx_data = json.loads(ctx.GetData())
        # The default env search paths are passed in through cmake test env vars
        self.assertEqual(
            ctx_data[PythonResolver.Tokens.searchPaths], ["/env/search/pathA", "/env/search/pathB"]
        )
        # Test env search paths
        os.environ["AR_SEARCH_PATHS"] = "/env/search/pathC:/env/search/pathD"
        ctx.LoadOrRefreshData()
        ctx_data = json.loads(ctx.GetData())
        self.assertEqual(
            ctx_data[PythonResolver.Tokens.searchPaths], ["/env/search/pathC", "/env/search/pathD"]
        )
        # Test custom search paths
        ctx.LoadOrRefreshData()
        ctx_data = json.loads(ctx.GetData())
        ctx_data[PythonResolver.Tokens.searchPaths].append("/custom/search/pathA")
        ctx.SetData(json.dumps(ctx_data))
        ctx_data = json.loads(ctx.GetData())
        self.assertEqual(
            ctx_data[PythonResolver.Tokens.searchPaths], ["/env/search/pathC", "/env/search/pathD", "/custom/search/pathA"]
        )
        # Test context (re-)creation
        os.environ["AR_SEARCH_PATHS"] = "/env/search/pathA:/env/search/pathB"
        ctx = PythonResolver.ResolverContext()
        ctx_data = json.loads(ctx.GetData())
        # Previous context editing should have no influence
        self.assertEqual(
            ctx_data[PythonResolver.Tokens.searchPaths], ["/env/search/pathA", "/env/search/pathB"]
        )

    def test_ResolverContextHash(self):
        self.assertEqual(
            hash(PythonResolver.ResolverContext()), hash(PythonResolver.ResolverContext())
        )
        # Currently only the pinning file path influences the hash
        self.assertNotEqual(
            hash(PythonResolver.ResolverContext("/some/mapping/file.usd")),
            hash(PythonResolver.ResolverContext()),
        )

    def test_ResolverContextRepr(self):
        self.assertEqual(
            repr(PythonResolver.ResolverContext("/some/mapping/file.usd")),
            "PythonResolver.ResolverContext('/some/mapping/file.usd')",
        )

    def test_ResolverContextMappingPairs(self):
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
                PythonResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)
            }
            mapping_layer.Export(mapping_file_path)

            # Test mapping file load
            ctx = PythonResolver.ResolverContext(mapping_file_path)
            ctx_data = json.loads(ctx.GetData())
            self.assertEqual(ctx.GetMappingFilePath(), mapping_file_path)
            self.assertEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs)
            # Test mapping add
            mapping_pairs_updated = {k: v for k, v in ctx_data[PythonResolver.Tokens.mappingPairs].items()}
            ctx_data[PythonResolver.Tokens.mappingPairs]["example/cube"] = "example/sphere"
            ctx_data[PythonResolver.Tokens.mappingPairs]["example/cone"] = "example/triangle"
            ctx_data[PythonResolver.Tokens.mappingPairs]["example/cylinder"] = "example/sphere"
            ctx.SetData(json.dumps(ctx_data))
            ctx_data = json.loads(ctx.GetData())
            self.assertNotEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs_updated)
            mapping_pairs_updated["example/cube"] = "example/sphere"
            mapping_pairs_updated["example/cone"] = "example/triangle"
            mapping_pairs_updated["example/cylinder"] = "example/sphere"
            self.assertEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs_updated)
            # Test mapping remove
            ctx_data[PythonResolver.Tokens.mappingPairs].pop("example/cone")
            ctx.SetData(json.dumps(ctx_data))
            ctx_data = json.loads(ctx.GetData())
            self.assertNotEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs_updated)
            mapping_pairs_updated.pop("example/cone")
            self.assertEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs_updated)
            ctx_data[PythonResolver.Tokens.mappingPairs] = { k:v for k, v in ctx_data[PythonResolver.Tokens.mappingPairs].items() if v != "example/sphere"}
            ctx.SetData(json.dumps(ctx_data))
            ctx_data = json.loads(ctx.GetData())
            self.assertNotEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs_updated)
            mapping_pairs_updated.pop("example/cube")
            mapping_pairs_updated.pop("example/cylinder")
            self.assertEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs_updated)
            # Test clear
            ctx_data[PythonResolver.Tokens.mappingPairs] = {}
            ctx.SetData(json.dumps(ctx_data))
            ctx_data = json.loads(ctx.GetData())
            self.assertEqual(ctx_data[PythonResolver.Tokens.mappingPairs], {})
            # Test refresh from file
            ctx.LoadOrRefreshData()
            ctx_data = json.loads(ctx.GetData())
            self.assertEqual(ctx_data[PythonResolver.Tokens.mappingPairs], mapping_pairs)

    def test_ResolverContextRegexExpressions(self):
        ctx = PythonResolver.ResolverContext()
        ctx_data = json.loads(ctx.GetData())
        # The default regex expression values are passed in through cmake test env vars
        self.assertEqual(ctx_data[PythonResolver.Tokens.mappingRegexExpression], "(v\d\d\d)")
        self.assertEqual(ctx_data[PythonResolver.Tokens.mappingRegexFormat], "v000")
        ctx_data[PythonResolver.Tokens.mappingRegexExpression] = "(cube)"
        ctx_data[PythonResolver.Tokens.mappingRegexFormat] = "Cube"
        ctx.SetData(json.dumps(ctx_data))
        ctx_data = json.loads(ctx.GetData())
        self.assertEqual(ctx_data[PythonResolver.Tokens.mappingRegexExpression], "(cube)")
        self.assertEqual(ctx_data[PythonResolver.Tokens.mappingRegexFormat], "Cube")


if __name__ == "__main__":
    unittest.main()
