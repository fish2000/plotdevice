
/// NSString to (char *)
#ifndef CSTRING
    #define CSTRING(NSStringRef) (char *)[NSStringRef UTF8String]
#endif

/// NSString to (PyString *)
#ifndef PYSTRING
    #define PYSTRING(NSStringRef) PyString_FromString((char *)[NSStringRef UTF8String])
#endif
