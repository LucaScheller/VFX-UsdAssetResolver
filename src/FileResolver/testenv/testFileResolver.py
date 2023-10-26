from __future__ import print_function
import tempfile
import os

from pxr import Ar, Sdf, Usd, Vt
from usdAssetResolver import FileResolver # We could put this in a separate test in the future.

import unittest
import shutil

class TestArDefaultResolver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Force Ar to use our FileResolver implementation.
        Ar.SetPreferredResolver('FileResolver')
        # Verify that the underlying resolver is the FileResolver
        assert(isinstance(Ar.GetUnderlyingResolver(), FileResolver.Resolver))

    def _test_CreateIdentifier(self):
        r = Ar.GetResolver()

        stage = Usd.Stage.CreateInMemory()
        context_collection = stage.GetPathResolverContext()
        context = context_collection.Get()[0]
        
        raise Exception(context.GetSearchPaths())

        ctx.GetMappingRegexExpression()               # Get the regex expression
        ctx.SetMappingRegexExpression(regex_str) # Set the regex expression
        ctx.GetMappingRegexFormat()                   # Get the regex expression substitution formatting
        ctx.SetMappingRegexFormat()                   # Set the regex expression substitution formatting

        # To print a full list of exposed methods:
        for attr in dir(FileResolver.ResolverContext):
            print(attr)


        ctx.GetSearchPaths()
        ctx.RefreshSearchPaths()
        ctx.GetEnvSearchPaths()
        ctx.GetCustomSearchPaths()
        ctx.SetCustomSearchPaths(searchPaths)

        def _RP(path = None):
            return Ar.ResolvedPath(os.path.abspath(path or ""))

        self.assertEqual('', r.CreateIdentifier(''))
        self.assertEqual('', r.CreateIdentifier('', _RP()))
        self.assertEqual('', r.CreateIdentifier('', _RP('AnchorAsset.txt')))

        # The identifier for an absolute path will always be that absolute
        # path normalized.
        self.assertPathsEqual(
            '/dir/AbsolutePath.txt',
            r.CreateIdentifier('/dir/AbsolutePath.txt'))

        self.assertPathsEqual(
            '/dir/AbsolutePath.txt',
            r.CreateIdentifier('/dir/AbsolutePath.txt', _RP('subdir/A.txt')))

        self.assertPathsEqual(
            '/dir/AbsolutePath.txt',
            r.CreateIdentifier('/dir/.//AbsolutePath.txt', _RP('subdir/A.txt')))

        # The identifier for a file-relative path (i.e. a relative path
        # starting with "./" or "../" is obtained by anchoring that path
        # to the given anchor, or the normalized file-relative path if no
        # anchor is given.
        self.assertPathsEqual(
            'subdir/FileRelative.txt',
            r.CreateIdentifier('./subdir/FileRelative.txt'))

        self.assertPathsEqual(
            os.path.abspath('dir/subdir/FileRelative.txt'),
            r.CreateIdentifier('./subdir/FileRelative.txt', _RP('dir/A.txt')))

        # Test look-here-first behavior for search-relative paths (i.e., 
        # relative paths that do not start with "./" or "../")
        #
        # If an asset exists at the location obtained by anchoring the 
        # relative path to the given anchor, the anchored path is used as
        # the identifier.
        if not os.path.isdir('dir/subdir'):
            os.makedirs('dir/subdir')
        with open('dir/subdir/Exists.txt', 'w') as f:
            pass
        
        self.assertPathsEqual(
            os.path.abspath('dir/subdir/Exists.txt'),
            r.CreateIdentifier('subdir/Exists.txt', _RP('dir/Anchor.txt')))

        # Otherwise, the search path is used as the identifier.
        self.assertPathsEqual(
            'subdir/Bogus.txt',
            r.CreateIdentifier('subdir/Bogus.txt', _RP('dir/Anchor.txt')))

    def _test_CreateIdentifierForNewAsset(self):
        r = Ar.GetResolver()

        def _RP(path = None):
            return Ar.ResolvedPath(os.path.abspath(path or ""))

        self.assertEqual(
            '', r.CreateIdentifierForNewAsset(''))
        self.assertEqual(
            '', r.CreateIdentifierForNewAsset('', _RP()))
        self.assertEqual(
            '', r.CreateIdentifierForNewAsset('', _RP('AnchorAsset.txt')))

        # The identifier for an absolute path will always be that absolute
        # path normalized.
        self.assertPathsEqual(
            '/dir/AbsolutePath.txt',
            r.CreateIdentifierForNewAsset('/dir/AbsolutePath.txt'))

        self.assertPathsEqual(
            '/dir/AbsolutePath.txt',
            r.CreateIdentifierForNewAsset(
                '/dir/AbsolutePath.txt', _RP('subdir/A.txt')))

        self.assertPathsEqual(
            '/dir/AbsolutePath.txt',
            r.CreateIdentifierForNewAsset(
                '/dir/.//AbsolutePath.txt', _RP('subdir/A.txt')))

        # The identifier for a relative path (file-relative or search-relative)
        # will always be the anchored abolute path.
        self.assertPathsEqual(
            os.path.abspath('subdir/FileRelative.txt'),
            r.CreateIdentifierForNewAsset(
                './subdir/FileRelative.txt'))

        self.assertPathsEqual(
            os.path.abspath('dir/subdir/FileRelative.txt'),
            r.CreateIdentifierForNewAsset(
                './subdir/FileRelative.txt', _RP('dir/Anchor.txt')))

        self.assertPathsEqual(
            os.path.abspath('subdir/SearchRel.txt'),
            r.CreateIdentifierForNewAsset(
                'subdir/SearchRel.txt'))

        self.assertPathsEqual(
            os.path.abspath('dir/subdir/SearchRel.txt'),
            r.CreateIdentifierForNewAsset(
                'subdir/SearchRel.txt', _RP('dir/Anchor.txt')))

    def _test_Resolve(self):
        testFileName = 'test_Resolve.txt'
        testFilePath = os.path.abspath(testFileName)
        with open(testFilePath, 'w') as ofp:
            print('Garbage', file=ofp)
        
        # XXX: Explicit conversion to str to accommodate change in
        # return type to Ar.ResolvedPath in Ar 2.0.
        resolvedPath = str(Ar.GetResolver().Resolve(testFileName))

        # The resolved path should be absolute.
        self.assertTrue(os.path.isabs(resolvedPath))
        self.assertPathsEqual(testFilePath, resolvedPath)

    def _test_ResolveSearchPaths(self):
        testDir = os.path.abspath('test1/test2')
        if os.path.isdir(testDir):
            shutil.rmtree(testDir)
        os.makedirs(testDir)

        testFileName = 'test_ResolveWithContext.txt'
        testFilePath = os.path.join(testDir, testFileName) 
        with open(testFilePath, 'w') as ofp:
            print('Garbage', file=ofp)
        
        resolver = Ar.GetResolver()

        self.assertPathsEqual(
            os.path.abspath('test1/test2/test_ResolveWithContext.txt'),
            resolver.Resolve('test2/test_ResolveWithContext.txt'))

        self.assertPathsEqual(
            os.path.abspath('test1/test2/test_ResolveWithContext.txt'),
            resolver.Resolve('test_ResolveWithContext.txt'))

    def _test_ResolveWithCache(self):
        testDir = os.path.abspath('testResolveWithCache/sub')
        if os.path.isdir(testDir):
            shutil.rmtree(testDir)
        os.makedirs(testDir)

        with open('testResolveWithCache/test.txt', 'w') as ofp:
            print('Test 1', file=ofp)

        with open('testResolveWithCache/sub/test.txt', 'w') as ofp:
            print('Test 2', file=ofp)
            
        resolver = Ar.GetResolver()

        # Set up a context that will search in the test root directory
        # first, then the subdirectory.
        context = Ar.DefaultResolverContext([
            os.path.abspath('testResolveWithCache'),
            os.path.abspath('testResolveWithCache/sub')])

        with Ar.ResolverContextBinder(context):
            with Ar.ResolverScopedCache():
                # Resolve should initially find the file in the test root
                # directory.
                self.assertPathsEqual(
                    os.path.abspath('testResolveWithCache/test.txt'),
                    resolver.Resolve('test.txt'))

                os.remove('testResolveWithCache/test.txt')

                # After removing the file from the test root directory,
                # Calling Resolve again will still return the same result
                # as before since a scoped cache is active.
                self.assertPathsEqual(
                    os.path.abspath('testResolveWithCache/test.txt'),
                    resolver.Resolve('test.txt'))

            # Once the caching scope is closed, Resolve should now return
            # the file from the subdirectory.
            self.assertPathsEqual(
                os.path.abspath('testResolveWithCache/sub/test.txt'),
                resolver.Resolve('test.txt'))

    def _test_ResolveWithContext(self):
        testDir = os.path.abspath('test3/test4')
        if os.path.isdir(testDir):
            shutil.rmtree(testDir)
        os.makedirs(testDir)
        
        testFileName = 'test_ResolveWithContext.txt'
        testFilePath = os.path.join(testDir, testFileName) 
        with open(testFilePath, 'w') as ofp:
            print('Garbage', file=ofp)
        
        resolver = Ar.GetResolver()
        context = Ar.DefaultResolverContext([
            os.path.abspath('test3'),
            os.path.abspath('test3/test4')
        ])

        self.assertPathsEqual(
            '', 
            resolver.Resolve('test4/test_ResolveWithContext.txt'))

        with Ar.ResolverContextBinder(context):
            self.assertPathsEqual(
                os.path.abspath('test3/test4/test_ResolveWithContext.txt'),
                resolver.Resolve('test4/test_ResolveWithContext.txt'))
            self.assertPathsEqual(
                os.path.abspath('test3/test4/test_ResolveWithContext.txt'),
                resolver.Resolve('test_ResolveWithContext.txt'))

        self.assertPathsEqual(
            '', 
            resolver.Resolve('test4/test_ResolveWithContext.txt'))

    def _test_ResolveWithDefaultAssetContext(self):
        assetFileName = 'test_Asset.txt'
        assetFilePath = os.path.abspath(assetFileName)
        with open(assetFilePath, 'w') as ofp:
            print('Garbage', file=ofp)

        testFileName = 'test_SiblingOfAsset.txt'
        testFilePath = os.path.abspath(testFileName)
        with open(testFilePath, 'w') as ofp:
            print('Garbage', file=ofp)
        
        # We use the non-absolute assetFileName to test the
        # cwd-anchoring behavior of CreateDefaultContextForAsset()
        context = Ar.GetResolver().CreateDefaultContextForAsset(assetFileName)
        with Ar.ResolverContextBinder(context):
            resolvedPath = Ar.GetResolver().Resolve(testFileName)

        self.assertPathsEqual(resolvedPath, testFilePath)

        # Make sure we get the same behavior using ConfigureResolverForAsset()
        if hasattr(Ar.Resolver, "ConfigureResolverForAsset"):
            Ar.GetResolver().ConfigureResolverForAsset(assetFileName)
            with Ar.ResolverContextBinder(Ar.GetResolver().CreateDefaultContext()):
                defaultResolvedPath = Ar.GetResolver().Resolve(testFileName)

            self.assertPathsEqual(defaultResolvedPath, testFilePath)

    def _test_ResolveForNewAsset(self):
        resolver  = Ar.GetResolver()

        # ResolveForNewAsset returns the path a new asset would be written
        # to for a given asset path. ArDefaultResolver assumes all asset paths
        # are filesystem paths, so this is just the absolute path of the
        # input.
        self.assertPathsEqual(
            resolver.ResolveForNewAsset('/test/path/1/newfile'),
            os.path.abspath('/test/path/1/newfile'))

        self.assertPathsEqual(
            resolver.ResolveForNewAsset('test/path/1/newfile'),
            os.path.abspath('test/path/1/newfile'))

        # This should work even if a file happens to already exist at the
        # computed path.
        testDir = os.path.abspath('ResolveForNewAsset')
        if os.path.isdir(testDir):
            shutil.rmtree(testDir)
        os.makedirs(testDir)

        testFileName = 'test_ResolveForNewAsset.txt'
        testFileAbsPath = os.path.join(testDir, testFileName)
        with open(testFileAbsPath, 'w') as ofp:
            print('Garbage', file=ofp)

        self.assertPathsEqual(
            resolver.ResolveForNewAsset(testFileAbsPath),
            testFileAbsPath)

        self.assertPathsEqual(
            resolver.ResolveForNewAsset(
                'ResolveForNewAsset/test_ResolveForNewAsset.txt'),
            testFileAbsPath)

    def test_ResolverContextSearchPaths(self):    
        ctx = FileResolver.ResolverContext()
        # The default env search paths are passed in through cmake test env vars
        self.assertEqual(ctx.GetSearchPaths(), ['/env/search/pathA', '/env/search/pathB'])
        self.assertEqual(ctx.GetEnvSearchPaths(), ['/env/search/pathA', '/env/search/pathB'])
        self.assertEqual(ctx.GetCustomSearchPaths(), [])
        # Test env search paths
        os.environ["AR_SEARCH_PATHS"] = "/env/search/pathC:/env/search/pathD"
        self.assertEqual(ctx.GetEnvSearchPaths(), ['/env/search/pathA', '/env/search/pathB'])
        ctx.RefreshSearchPaths()
        self.assertEqual(ctx.GetEnvSearchPaths(), ['/env/search/pathC', '/env/search/pathD'])
        # Test custom search paths
        ctx.SetCustomSearchPaths(['/custom/search/pathA', '/custom/search/pathB'])
        self.assertEqual(ctx.GetSearchPaths(), ['/env/search/pathC', '/env/search/pathD'])
        ctx.RefreshSearchPaths()
        self.assertEqual(ctx.GetSearchPaths(), ['/env/search/pathC', '/env/search/pathD', '/custom/search/pathA', '/custom/search/pathB'])
        # Test context (re-)creation
        os.environ["AR_SEARCH_PATHS"] = "/env/search/pathA:/env/search/pathB"
        ctx = FileResolver.ResolverContext()
        # Previous context editing should have no influence
        self.assertEqual(ctx.GetSearchPaths(), ['/env/search/pathA', '/env/search/pathB'])

    def test_ResolverContextHash(self):  
        self.assertEqual(
            hash(FileResolver.ResolverContext()),
            hash(FileResolver.ResolverContext())
        )
        # Currently only the pinning file path influences the hash
        search_paths = ['/custom/search/pathA', '/custom/search/pathB']
        self.assertEqual(
            hash(FileResolver.ResolverContext(search_paths)),
            hash(FileResolver.ResolverContext())
        )
        self.assertNotEqual(
            hash(FileResolver.ResolverContext("/some/mapping/file.usd")),
            hash(FileResolver.ResolverContext())
        )

    def test_ResolverContextRepr(self):  
        self.assertEqual(
            repr(FileResolver.ResolverContext("/some/mapping/file.usd")),
            "FileResolver.ResolverContext('/some/mapping/file.usd')"
        )

    def test_ResolverContextMappingPairs(self):  
        with tempfile.TemporaryDirectory() as temp_dir_path:
            # Create mapping file
            mapping_file_path = os.path.join(temp_dir_path, "mapping.usd")

            mapping_layer = Sdf.Layer.CreateAnonymous()
            mapping_pairs = {'assets/assetA/assetA.usd':'assets/assetA/assetA_v005.usd', 'shots/shotA/shotA_v000.usd':'shots/shotA/shotA_v003.usd'}
            mapping_array = []
            for source_path, target_path in mapping_pairs.items():
                mapping_array.extend([source_path, target_path])
            mapping_layer.customLayerData = {FileResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)}
            mapping_layer.Export(mapping_file_path)

            # Test mapping file load
            ctx = FileResolver.ResolverContext(mapping_file_path)
            self.assertEqual(ctx.GetMappingFilePath(), mapping_file_path)
            self.assertEqual(ctx.GetMappingPairs(), mapping_pairs)
            # Test mapping add
            mapping_pairs_updated = {k:v for k, v in ctx.GetMappingPairs().items()}
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

    def test_ResolverContextRegexExpressions(self):  
        ctx = FileResolver.ResolverContext()
        # The default regex expression values are passed in through cmake test env vars
        self.assertEqual(ctx.GetMappingRegexExpression(), "(v\d\d\d)")
        self.assertEqual(ctx.GetMappingRegexFormat(), "v000")
        ctx.SetMappingRegexExpression("(cube)")
        ctx.SetMappingRegexFormat("Cube")
        self.assertEqual(ctx.GetMappingRegexExpression(), "(cube)")
        self.assertEqual(ctx.GetMappingRegexFormat(), "Cube")


if __name__ == '__main__':
    unittest.main()
