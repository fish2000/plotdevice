from os import getcwd
from os.path import dirname, join
# from distutils.core import setup, Extension
from setuptools import setup, find_packages
from setuptools.extension import Extension

frameworks = join(dirname(dirname(getcwd())), 'Frameworks')
gpuimage_libs = join(frameworks,  'GPUImage.framework', 'Versions', 'A')
gpuimage_headers = join(gpuimage_libs, 'Headers')

tensor = Extension('tensor',
    sources=[
        'module.m',
        'Filter.m'],
    extra_compile_args=[
        '-Wno-error=unused-command-line-argument-hard-error-in-future',
        '-Qunused-arguments',
        '-F%s' % frameworks],
    extra_link_args=[
        '-Wno-error=unused-command-line-argument-hard-error-in-future',
        '-L%s' % gpuimage_libs,
        '-F%s' % frameworks,
        '-framework', 'AppKit',
        '-framework', 'Foundation',
        '-framework', 'Quartz',
        '-framework', 'Security',
        '-framework', 'CoreMedia',
        '-framework', 'GPUImage'])

setup(name="tensor",
       version="1.0",
       author="fish2k",
       description="GPU-based image processing",
       ext_modules=[tensor],
       include_dirs=[gpuimage_headers])