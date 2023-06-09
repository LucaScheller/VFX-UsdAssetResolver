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
  if(DEFINED AR_BOOST_NAMESPACE)
    target_compile_definitions(${target}
      PRIVATE
        AR_BOOST_NAMESPACE=${AR_BOOST_NAMESPACE}
    )
  endif()
endfunction(set_boost_namespace)