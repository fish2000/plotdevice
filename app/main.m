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
        NSString *mainFilePath = [[NSBundle mainBundle] pathForResource:@"plotdevice-app" ofType:@"py"];
        NSString *mainFileName = [mainFilePath lastPathComponent];
        return PyRun_SimpleFile(fopen([mainFilePath UTF8String], "r"), (char *)[mainFileName UTF8String]);
    }
}
