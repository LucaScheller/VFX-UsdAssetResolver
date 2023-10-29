#include "resolverTokens.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)

using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE

namespace {
    class _WrapStaticToken {
        public:
            _WrapStaticToken(const TfToken* token) : _token(token) { }
            std::string operator()() const
            {
                return _token->GetString();
            }
        private:
            const TfToken* _token;
    };

    template <typename T>
    void
    _AddToken(T& cls, const char* name, const TfToken& token)
    {
        cls.add_static_property(name,
                                make_function(_WrapStaticToken(&token),
                                return_value_policy<return_by_value>(),
                                AR_BOOST_NAMESPACE::mpl::vector1<std::string>()));
    }
}

void wrapResolverTokens()
{
    class_<PythonResolverTokensType, AR_BOOST_NAMESPACE::noncopyable>
        cls("Tokens", no_init);
    _AddToken(cls, "mappingPairs", PythonResolverTokens->mappingPairs);
    _AddToken(cls, "mappingRegexExpression", PythonResolverTokens->mappingRegexExpression);
    _AddToken(cls, "mappingRegexFormat", PythonResolverTokens->mappingRegexFormat);
    _AddToken(cls, "searchPaths", PythonResolverTokens->searchPaths);
}