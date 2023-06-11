
class PythonResolver():
    @staticmethod
    def _CreateIdentifier(assetPath, anchorAssetPath):
        print("_CreateIdentifier")
        return "_CreateIdentifier"
    @staticmethod
    def _CreateIdentifierForNewAsset(assetPath, anchorAssetPath):
        print("_CreateIdentifierForNewAsset")
        return "_CreateIdentifierForNewAsset"
    @staticmethod
    def _Resolve(assetPath):
        print("_Resolve")
    @staticmethod
    def _ResolveForNewAsset(assetPath):
        print("_ResolveForNewAsset")
    @staticmethod
    def _CreateDefaultContext(assetPath):
        print("_CreateDefaultContext")
    @staticmethod
    def _CreateDefaultContextForAsset(assetPath):
        print("_CreateDefaultContextForAsset")
    @staticmethod
    def _IsContextDependentPath(assetPath):
        print("_IsContextDependentPath")
    @staticmethod
    def _RefreshContext(context):
        print("_RefreshContext")
    @staticmethod
    def _GetModificationTimestamp(assetPath, resolvedPath):
        print("_GetModificationTimestamp")