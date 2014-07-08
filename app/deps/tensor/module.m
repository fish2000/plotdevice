#import <Python.h>

PyMethodDef methods[] = {
  { NULL, NULL },
};

PyMODINIT_FUNC inittensorlib() {
    (void)Py_InitModule("tensorlib", methods);
}

