from __future__ import print_function
import tempfile
import os
import unittest

from pxr import Ar, Sdf, Usd, Vt
from usdAssetResolver import CachedResolver

import PythonExpose

class TestArResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force Ar to use our CachedResolver implementation.
        Ar.SetPreferredResolver("CachedResolver")
        # Verify that the underlying resolver is the CachedResolver
        assert isinstance(Ar.GetUnderlyingResolver(), CachedResolver.Resolver)

    def test_CreateIdentifier(self):
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

        self.assertEqual(
            "project/assets/asset/path.usd",
            resolver.CreateIdentifier(
                "project/assets/asset/path.usd",
                Ar.ResolvedPath("/some/absolute/path.usd"),
            ),
        )

    def test_CreateRelativeIdentifier(self):
        resolver = Ar.GetResolver()
        cached_resolver = Ar.GetUnderlyingResolver()

        # Test expose relative path identifier state and cache
        self.assertEqual(cached_resolver.GetExposeRelativePathIdentifierState(), False)

        cached_resolver.SetExposeRelativePathIdentifierState(True)
        self.assertEqual(cached_resolver.GetExposeRelativePathIdentifierState(), True)

        cached_resolver.AddCachedRelativePathIdentifierPair("/some/absolute/path.usd", "some/relative/path.usd?/some/absolute")
        self.assertEqual(cached_resolver.GetCachedRelativePathIdentifierPairs(),
                         {'/some/absolute/path.usd': 'some/relative/path.usd?/some/absolute'})
        
        cached_resolver.SetExposeRelativePathIdentifierState(True)
        self.assertEqual(cached_resolver.GetCachedRelativePathIdentifierPairs(),
                         {'/some/absolute/path.usd': 'some/relative/path.usd?/some/absolute'})

        cached_resolver.SetExposeRelativePathIdentifierState(False)
        self.assertEqual(cached_resolver.GetCachedRelativePathIdentifierPairs(), {})

        cached_resolver.AddCachedRelativePathIdentifierPair("/some/absolute/path.usd", "some/relative/path.usd?/some/absolute")
        cached_resolver.RemoveCachedRelativePathIdentifierByKey("/some/absolute/path.usd")
        self.assertEqual(cached_resolver.GetCachedRelativePathIdentifierPairs(),{})
        
        cached_resolver.AddCachedRelativePathIdentifierPair("/some/absolute/path.usd", "some/relative/path.usd?/some/absolute")
        cached_resolver.RemoveCachedRelativePathIdentifierByValue("some/relative/path.usd?/some/absolute")
        self.assertEqual(cached_resolver.GetCachedRelativePathIdentifierPairs(),{})

        cached_resolver.AddCachedRelativePathIdentifierPair("/some/absolute/path.usd", "some/relative/path.usd?/some/absolute")
        cached_resolver.ClearCachedRelativePathIdentifierPairs()
        self.assertEqual(cached_resolver.GetCachedRelativePathIdentifierPairs(),{})

        # Reset UnitTestHelper
        PythonExpose.UnitTestHelper.reset()
        cached_resolver.SetExposeRelativePathIdentifierState(True)

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
            "relativePath|./some/relative/path.usd?/some/absolute/",
            resolver.CreateIdentifier(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/absolute/")
            ),
        )
        self.assertEqual(
            "relativePath|./some/relative/path.usd?/some/absolute/",
            resolver.CreateIdentifier(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/absolute/path.usd")
            ),
        )
        self.assertEqual(
            PythonExpose.UnitTestHelper.create_relative_path_identifier_call_counter,
            1
        )

        self.assertEqual(
            "relativePath|./some/relative/path.usd?/some/other/absolute/path.usd",
            resolver.CreateIdentifier(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/other/absolute/path.usd")
            ),
        )
        self.assertEqual(
            "relativePath|./some/relative/path.usd?/some/other/absolute/path.usd",
            resolver.CreateIdentifier(
                "./some/relative/path.usd", Ar.ResolvedPath("/some/other/absolute/path.usd")
            ),
        )
        self.assertEqual(
            PythonExpose.UnitTestHelper.create_relative_path_identifier_call_counter,
            2
        )

        self.assertEqual(
            "relativePath|../some/relative/path.usd?/some/absolute/",
            resolver.CreateIdentifier(
                "../some/relative/path.usd", Ar.ResolvedPath("/some/absolute/")
            ),
        )
        self.assertEqual(
            "relativePath|../some/relative/path.usd?/some/absolute/",
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

        self.assertEqual(
            "project/assets/asset/path.usd",
            resolver.CreateIdentifier(
                "project/assets/asset/path.usd",
                Ar.ResolvedPath("/some/absolute/path.usd"),
            ),
        )

        cached_resolver.SetExposeRelativePathIdentifierState(False)

    def test_CreateIdentifierForNewAsset(self):
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

    def test_CreateRelativeIdentifierWithResolverCachingMechanism(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Get resolver
            resolver = Ar.GetResolver()
            cached_resolver = Ar.GetUnderlyingResolver()
            # Reset UnitTestHelper
            PythonExpose.UnitTestHelper.reset(current_directory_path=temp_dir_path)
            # Create files
            asset_a_identifier = "assetA.usd"
            asset_a_layer_file_path = os.path.join(temp_dir_path, asset_a_identifier)
            Sdf.Layer.CreateAnonymous().Export(asset_a_layer_file_path)
            asset_b_identifier = "assetB.usd"
            asset_b_layer_file_path = os.path.join(temp_dir_path, asset_b_identifier)
            Sdf.Layer.CreateAnonymous().Export(asset_b_layer_file_path)
            asset_c_identifier = "assetC.usd"
            asset_c_layer_file_path = os.path.join(temp_dir_path, asset_c_identifier)
            Sdf.Layer.CreateAnonymous().Export(asset_c_layer_file_path)
            self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 0)

            # Check that native relative file path resolving works
            # cached_resolver.SetExposeRelativePathIdentifierState(False) # The default is False
            asset_a_relative_layer = Sdf.Layer.FindOrOpenRelativeToLayer(Sdf.Layer.FindOrOpen(asset_b_layer_file_path), "./" + asset_a_identifier)
            self.assertEqual(asset_a_layer_file_path, asset_a_relative_layer.identifier)

            # Create context
            ctx = CachedResolver.ResolverContext()
            self.assertEqual(PythonExpose.UnitTestHelper.context_initialize_call_counter, 1)
            self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 0)
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                # Resolve
                layer_identifier = "layer.usd"
                resolver.Resolve(layer_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 1)
                # See PythonExpose.py for more info
                layer_identifier = "unittest.usd"
                resolver.Resolve(layer_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                # Our unittest.usd resolve call caches these test paths,
                # see PythonExpose.py for more info
                resolver.Resolve(layer_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                self.assertEqual(ctx.GetCachingPairs(),
                                 {'assetA.usd': asset_a_layer_file_path,
                                  'assetB.usd': asset_b_layer_file_path,
                                  'layer.usd': '/some/path/to/a/file.usd',
                                  'unittest.usd': '/some/path/to/a/file.usd',
                                  'shot.usd': '/some/path/to/a/file.usd'})
                # Verify that mapping pairs have higher loading priority than
                # caching pairs.
                ctx.AddCachingPair(asset_c_identifier, asset_c_layer_file_path)
                self.assertEqual(resolver.Resolve(asset_c_identifier), asset_c_layer_file_path)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                ctx.AddMappingPair(asset_c_identifier, asset_a_layer_file_path)
                self.assertEqual(resolver.Resolve(asset_c_identifier), asset_a_layer_file_path)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                ctx.RemoveMappingByKey(asset_c_identifier)
                self.assertEqual(resolver.Resolve(asset_c_identifier), asset_c_layer_file_path)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                # Check that re-init works
                mapping_file_path = os.path.join(temp_dir_path, "mapping.usd")
                mapping_layer = Sdf.Layer.CreateAnonymous()
                mapping_pairs = {
                    asset_a_identifier: asset_c_layer_file_path,
                }
                mapping_array = []
                for source_path, target_path in mapping_pairs.items():
                    mapping_array.extend([source_path, target_path])
                mapping_layer.customLayerData = {
                    CachedResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)
                }
                mapping_layer.Export(mapping_file_path)
                ctx.SetMappingFilePath(mapping_file_path)
                ctx.ClearAndReinitialize()
                self.assertEqual(ctx.GetMappingPairs(), {asset_a_identifier: asset_c_layer_file_path})
                self.assertEqual(PythonExpose.UnitTestHelper.context_initialize_call_counter, 2)

                # Check that exposed relative file path resolving works
                ctx.SetMappingFilePath("")
                ctx.ClearAndReinitialize()
                cached_resolver.SetExposeRelativePathIdentifierState(True)
                self.assertEqual(PythonExpose.UnitTestHelper.create_relative_path_identifier_call_counter, 0)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                asset_a_relative_layer = Sdf.Layer.FindOrOpenRelativeToLayer(Sdf.Layer.FindOrOpen(asset_b_layer_file_path), "./" + asset_a_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.create_relative_path_identifier_call_counter, 1)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 3)
                self.assertEqual(asset_a_relative_layer, Sdf.Layer.FindOrOpen(asset_a_layer_file_path))
                cached_resolver.SetExposeRelativePathIdentifierState(False)

    def test_Resolve(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create files
            layer_identifier = "layer.usd"
            layer_file_path = os.path.join(temp_dir_path, layer_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_file_path)
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.AddCachingPair(layer_identifier, layer_file_path)
            # Get resolver
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                resolved_path = resolver.Resolve(layer_identifier)
                self.assertEqual(resolved_path.GetPathString(), layer_file_path)
                self.assertTrue(os.path.isabs(resolved_path.GetPathString()))
                resolved_path = resolver.Resolve("example.usd")
                self.assertEqual(resolved_path.GetPathString(), "/some/path/to/a/file.usd")
                resolved_path = resolver.Resolve("/some/invalid/path.usd")
                self.assertEqual(resolved_path.GetPathString(), "")
                resolved_path = resolver.Resolve(layer_file_path)
                self.assertEqual(resolved_path.GetPathString(), layer_file_path)

    def test_ResolveAbsoluteIdentifier(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Get resolver
            resolver = Ar.GetResolver()
            cached_resolver = Ar.GetUnderlyingResolver()
            # Create files
            layer_a_identifier = "layer_a.usd"
            layer_a_file_path = os.path.join(temp_dir_path, layer_a_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_a_file_path)
            layer_b_identifier = "layer_b.usd"
            layer_b_file_path = os.path.join(temp_dir_path, layer_b_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_b_file_path)
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.AddCachingPair(layer_a_identifier, layer_a_file_path)
            ctx.AddCachingPair(layer_b_identifier, layer_b_file_path)
            ctx.AddCachingPair(layer_b_file_path, layer_a_file_path)
            # Reset UnitTestHelper
            PythonExpose.UnitTestHelper.reset(current_directory_path=temp_dir_path)
            with Ar.ResolverContextBinder(ctx):
                resolved_path = resolver.Resolve(layer_a_identifier)
                self.assertEqual(resolved_path.GetPathString(), layer_a_file_path)
                self.assertTrue(os.path.isabs(resolved_path.GetPathString()))
                resolved_path = resolver.Resolve(layer_b_identifier)
                self.assertEqual(resolved_path.GetPathString(), layer_b_file_path)
                self.assertTrue(os.path.isabs(resolved_path.GetPathString()))
                # Check that exposed absolute file path resolving works
                resolved_path = resolver.Resolve(layer_b_file_path)
                self.assertEqual(resolved_path.GetPathString(), layer_b_file_path)
                self.assertTrue(os.path.isabs(resolved_path.GetPathString()))
                cached_resolver.SetExposeAbsolutePathIdentifierState(True)
                resolved_path = resolver.Resolve(layer_b_file_path)
                self.assertEqual(resolved_path.GetPathString(), layer_a_file_path)
                self.assertTrue(os.path.isabs(resolved_path.GetPathString()))
                cached_resolver.SetExposeAbsolutePathIdentifierState(False)

    def test_ResolveForNewAsset(self):
        resolver = Ar.GetResolver()

        layer_identifier = "layer.usd"
        layer_file_path = os.path.join(os.getcwd(), layer_identifier)
        resolved_path = resolver.ResolveForNewAsset(layer_identifier)
        self.assertEqual(resolved_path.GetPathString(), layer_file_path)

        layer_identifier = "../layer.usd"
        layer_file_path = os.path.abspath(os.path.join(os.getcwd(), layer_identifier))
        resolved_path = resolver.ResolveForNewAsset(layer_identifier)
        self.assertEqual(resolved_path.GetPathString(), layer_file_path)

    def test_ResolveWithScopedCache(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create files
            layer_identifier = "layer.usd"
            layer_file_path = os.path.join(temp_dir_path, layer_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_file_path)
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.AddCachingPair(layer_identifier, layer_file_path)
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
                    ctx.RemoveCachingByKey(layer_identifier)
                    os.remove(layer_file_path)
                    # Query cached result
                    self.assertEqual(
                        os.path.abspath(layer_file_path),
                        resolver.Resolve(layer_identifier),
                    )
                # Uncached result should now return the default PythonExpose.py result
                self.assertEqual(resolver.Resolve(layer_identifier), "/some/path/to/a/file.usd")

    def test_ResolverCachingMechanism(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Get resolver
            resolver = Ar.GetResolver()
            # Reset UnitTestHelper
            PythonExpose.UnitTestHelper.reset(current_directory_path=temp_dir_path)
            # Create files
            asset_a_identifier = "assetA.usd"
            asset_a_layer_file_path = os.path.join(temp_dir_path, asset_a_identifier)
            Sdf.Layer.CreateAnonymous().Export(asset_a_layer_file_path)
            asset_b_identifier = "assetB.usd"
            asset_b_layer_file_path = os.path.join(temp_dir_path, asset_b_identifier)
            Sdf.Layer.CreateAnonymous().Export(asset_b_layer_file_path)
            asset_c_identifier = "assetC.usd"
            asset_c_layer_file_path = os.path.join(temp_dir_path, asset_c_identifier)
            Sdf.Layer.CreateAnonymous().Export(asset_c_layer_file_path)
            self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 0)
            # Create context
            ctx = CachedResolver.ResolverContext()
            self.assertEqual(PythonExpose.UnitTestHelper.context_initialize_call_counter, 1)
            self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 0)
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                # Resolve
                layer_identifier = "layer.usd"
                resolver.Resolve(layer_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 1)
                # See PythonExpose.py for more info
                layer_identifier = "unittest.usd"
                resolver.Resolve(layer_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                # Our unittest.usd resolve call caches these test paths,
                # see PythonExpose.py for more info
                resolver.Resolve(layer_identifier)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                self.assertEqual(ctx.GetCachingPairs(),
                                 {'assetA.usd': asset_a_layer_file_path,
                                  'assetB.usd': asset_b_layer_file_path,
                                  'layer.usd': '/some/path/to/a/file.usd',
                                  'unittest.usd': '/some/path/to/a/file.usd',
                                  'shot.usd': '/some/path/to/a/file.usd'})
                # Verify that mapping pairs have higher loading priority than
                # caching pairs.
                ctx.AddCachingPair(asset_c_identifier, asset_c_layer_file_path)
                self.assertEqual(resolver.Resolve(asset_c_identifier), asset_c_layer_file_path)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                ctx.AddMappingPair(asset_c_identifier, asset_a_layer_file_path)
                self.assertEqual(resolver.Resolve(asset_c_identifier), asset_a_layer_file_path)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                ctx.RemoveMappingByKey(asset_c_identifier)
                self.assertEqual(resolver.Resolve(asset_c_identifier), asset_c_layer_file_path)
                self.assertEqual(PythonExpose.UnitTestHelper.resolve_and_cache_call_counter, 2)
                # Check that re-init works
                mapping_file_path = os.path.join(temp_dir_path, "mapping.usd")
                mapping_layer = Sdf.Layer.CreateAnonymous()
                mapping_pairs = {
                    asset_a_identifier: asset_c_layer_file_path,
                }
                mapping_array = []
                for source_path, target_path in mapping_pairs.items():
                    mapping_array.extend([source_path, target_path])
                mapping_layer.customLayerData = {
                    CachedResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)
                }
                mapping_layer.Export(mapping_file_path)
                ctx.SetMappingFilePath(mapping_file_path)
                ctx.ClearAndReinitialize()
                self.assertEqual(ctx.GetMappingPairs(), {asset_a_identifier: asset_c_layer_file_path})
                self.assertEqual(PythonExpose.UnitTestHelper.context_initialize_call_counter, 2)

    def test_ResolveWithContext(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create files
            layer_v001_identifier = "layer_v001.usd"
            layer_v001_file_path = os.path.join(temp_dir_path, layer_v001_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_v001_file_path)
            layer_v002_identifier = "layer_v002.usd"
            layer_v002_file_path = os.path.join(temp_dir_path, layer_v002_identifier)
            Sdf.Layer.CreateAnonymous().Export(layer_v002_file_path)
            # Create context
            ctx = CachedResolver.ResolverContext()
            ctx.AddMappingPair(layer_v001_identifier, layer_v002_file_path)
            # Get resolver
            resolver = Ar.GetResolver()
            with Ar.ResolverContextBinder(ctx):
                resolved_path = resolver.Resolve(layer_v001_identifier)
                self.assertEqual(resolved_path.GetPathString(), layer_v002_file_path)

    def test_ResolveWithCacheContextRefresh(self):
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

    def test_ResolverContextHash(self):
        self.assertEqual(
            hash(CachedResolver.ResolverContext()), hash(CachedResolver.ResolverContext())
        )
        # Currently only the pinning file path influences the hash
        self.assertNotEqual(
            hash(CachedResolver.ResolverContext("/some/mapping/file.usd")),
            hash(CachedResolver.ResolverContext()),
        )

    def test_ResolverContextRepr(self):
        self.assertEqual(
            repr(CachedResolver.ResolverContext("/some/mapping/file.usd")),
            "CachedResolver.ResolverContext('/some/mapping/file.usd')",
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

    def test_ResolverContextCachingPairs(self):
        with tempfile.TemporaryDirectory() as temp_dir_path:
            ctx = CachedResolver.ResolverContext()
            # Test caching add
            caching_pairs_updated = {k: v for k, v in ctx.GetCachingPairs().items()}
            ctx.AddCachingPair("example/cube", "example/sphere")
            ctx.AddCachingPair("example/cone", "example/triangle")
            ctx.AddCachingPair("example/cylinder", "example/sphere")
            self.assertNotEqual(ctx.GetCachingPairs(), caching_pairs_updated)
            caching_pairs_updated["example/cube"] = "example/sphere"
            caching_pairs_updated["example/cone"] = "example/triangle"
            caching_pairs_updated["example/cylinder"] = "example/sphere"
            self.assertEqual(ctx.GetCachingPairs(), caching_pairs_updated)
            # Test mapping remove
            ctx.RemoveCachingByKey("example/cone")
            self.assertNotEqual(ctx.GetCachingPairs(), caching_pairs_updated)
            caching_pairs_updated.pop("example/cone")
            self.assertEqual(ctx.GetCachingPairs(), caching_pairs_updated)

            ctx.RemoveCachingByValue("example/sphere")
            self.assertNotEqual(ctx.GetCachingPairs(), caching_pairs_updated)
            caching_pairs_updated.pop("example/cube")
            caching_pairs_updated.pop("example/cylinder")
            self.assertEqual(ctx.GetCachingPairs(), caching_pairs_updated)
            # Test clear
            ctx.ClearCachingPairs()
            self.assertEqual(ctx.GetCachingPairs(), {})
            # Test refresh from file
            ctx.ClearAndReinitialize()
            self.assertEqual(ctx.GetCachingPairs(), {'shot.usd': '/some/path/to/a/file.usd'})


if __name__ == "__main__":
    unittest.main()
