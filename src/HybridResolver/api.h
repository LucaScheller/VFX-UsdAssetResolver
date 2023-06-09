#ifndef AR_HYBRIDRESOLVER_API_H
#define AR_HYBRIDRESOLVER_API_H

#include "pxr/base/arch/export.h"

#if defined(PXR_STATIC)
#   define AR_HYBRIDRESOLVER_API
#   define AR_HYBRIDRESOLVER_API_TEMPLATE_CLASS(...)
#   define AR_HYBRIDRESOLVER_API_TEMPLATE_STRUCT(...)
#   define AR_HYBRIDRESOLVER_LOCAL
#else
#   if defined(AR_HYBRIDRESOLVER_EXPORTS)
#       define AR_HYBRIDRESOLVER_API ARCH_EXPORT
#       define AR_HYBRIDRESOLVER_API_TEMPLATE_CLASS(...) ARCH_EXPORT_TEMPLATE(class, __VA_ARGS__)
#       define AR_HYBRIDRESOLVER_API_TEMPLATE_STRUCT(...) ARCH_EXPORT_TEMPLATE(struct, __VA_ARGS__)
#   else
#       define AR_HYBRIDRESOLVER_API ARCH_IMPORT
#       define AR_HYBRIDRESOLVER_API_TEMPLATE_CLASS(...) ARCH_IMPORT_TEMPLATE(class, __VA_ARGS__)
#       define AR_HYBRIDRESOLVER_API_TEMPLATE_STRUCT(...) ARCH_IMPORT_TEMPLATE(struct, __VA_ARGS__)
#   endif
#   define AR_HYBRIDRESOLVER_LOCAL ARCH_HIDDEN
#endif

#endif // AR_HYBRIDRESOLVER_API_H
