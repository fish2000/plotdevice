#import <Python.h>

PyMethodDef methods[] = {
  {NULL, NULL},
};

void inittensor()
  {
    (void)Py_InitModule("tensor", methods);
  }

