from os import getcwd
from os.path import dirname, join
from setuptools import setup
from setuptools.extension import Extension

frameworks = join(dirname(dirname(getcwd())), 'Frameworks')
gpuimage_libs = join(frameworks,  'GPUImage.framework', 'Versions', 'A')
gpuimage_headers = join(gpuimage_libs, 'Headers')

tensorlib = Extension('tensorlib',
    sources=[
        'module.m',
        'FilterBase.m',
        'ColorInvertFilter.m',
        'HalftoneFilter.m',
        'MissEtikateFilter.m',
        'PolkaDotFilter.m',
        'SepiaFilter.m',
        'SoftEleganceFilter.m',
        'VignetteFilter.m'],
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

setup(name="tensorlib",
       version="1.0",
       author="fish2k",
       description="GPU-based image processing",
       ext_modules=[tensorlib],
       include_dirs=[gpuimage_headers])