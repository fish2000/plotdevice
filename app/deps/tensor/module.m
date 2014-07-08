#import <Python.h>

/*
 * Stub python module declaration --
 * Allows Objective-C classes with which it is linked
 * to be found and loaded from python via `objc.lookUpClass()`
 */

PyMethodDef methods[] = {
  { NULL, NULL },
};

PyMODINIT_FUNC inittensorlib() {
    (void)Py_InitModule("tensorlib", methods);
}

