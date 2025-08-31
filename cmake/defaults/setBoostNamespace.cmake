# Boost can be namespaced with bcp
# https://www.boost.org/doc/libs/1_70_0/tools/bcp/doc/html/index.html
# This changes:
# - the root folder name of the C++ headers
# - the shared libraries names
# - the symbol namespaces
#
# This function allows to define a compile symbol BOOST_NAMESPACE. It is then
# used in boost_include_wrapper.h to define a BOOST_INCLUDE macro that helps
# with setting the proper boost root folder for files to include.
function(set_boost_namespace target)
  target_compile_definitions(${target}
    PRIVATE
      AR_BOOST_NAMESPACE=${AR_BOOST_NAMESPACE}
  )
endfunction(set_boost_namespace)

# As certain USD distributions ship with pxr_boost (where the folder is still called 'boost'),
# we have to treat the folder for header imports separately.
function(set_boost_folder_namespace target)
  target_compile_definitions(${target}
    PRIVATE
      AR_BOOST_FOLDER_NAMESPACE=${AR_BOOST_FOLDER_NAMESPACE}
  )
endfunction(set_boost_folder_namespace)
# We also need to change code logic, as pxr_boost transferred over certain boost (non-python) files.
function(set_boost_pxr_external_exists target)
  target_compile_definitions(${target}
    PRIVATE
      AR_BOOST_PXR_EXTERNAL_EXISTS=${AR_BOOST_PXR_EXTERNAL_EXISTS}
  )
endfunction(set_boost_pxr_external_exists)
