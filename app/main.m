#import <Python.h>

#ifndef PLOTDEVICE_PYTHON
    #define PLOTDEVICE_PYTHON "/usr/bin/python"
#endif

int main(int argc, char *argv[])
{
    @autoreleasepool{
        Py_SetProgramName(PLOTDEVICE_PYTHON);
        Py_Initialize();
        PySys_SetArgv(argc, (char **)argv);
        
        NSString *mainBundlePath = [[NSBundle mainBundle] bundlePath];
        NSString *bundleSitePackages = [mainBundlePath stringByAppendingPathComponent:@"Contents/Resources/python"];
        NSString *bundlePyObjC = [bundleSitePackages stringByAppendingPathComponent:@"PyObjC"];
        
        PyObject *sys = PyImport_ImportModule("sys");
        PyObject *path = PyObject_GetAttrString(sys, "path");
        PyList_Insert(path, (Py_ssize_t)0,
            PyString_FromString(
                (char *)[bundleSitePackages UTF8String]));
        PyList_Insert(path, (Py_ssize_t)0,
            PyString_FromString(
                (char *)[bundlePyObjC UTF8String]));
        
        NSString *mainFilePath = [[NSBundle mainBundle] pathForResource:@"plotdevice-app" ofType:@"py"];
        NSString *mainFileName = [mainFilePath lastPathComponent];
        return PyRun_SimpleFile(fopen([mainFilePath UTF8String], "r"), (char *)[mainFileName UTF8String]);
    }
}
