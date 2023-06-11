#include <string>
#include <iostream>

#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/sdf/namespaceEdit.h>
#include <pxr/usd/sdf/path.h>


int main()
{
  auto layer = pxr::SdfLayer::FindOrOpen("testPinning.usda");
}
