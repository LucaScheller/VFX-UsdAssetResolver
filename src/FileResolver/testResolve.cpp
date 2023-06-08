#include <string>
#include <iostream>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/sdf/namespaceEdit.h>
#include <pxr/usd/sdf/path.h>


namespace python = AR_BOOST_NAMESPACE::python;

int main()
{
  auto layer = pxr::SdfLayer::FindOrOpen("./input.usda");

  std::cout << layer->GetIdentifier() << std::endl;
}
