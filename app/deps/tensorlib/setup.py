from __future__ import print_function

from pprint import pprint
from os import getcwd, walk
from os.path import splitext, dirname, join
from setuptools import setup
from setuptools.extension import Extension

frameworks = join(dirname(dirname(getcwd())), 'Frameworks')
gpuimage_libs = join(frameworks,  'GPUImage.framework', 'Versions', 'A')
gpuimage_headers = join(gpuimage_libs, 'Headers')

def find_filters(base_path="filters"):
    filters = dict()
    for root_path, dirs, files in walk(base_path):
        for file_name in files:
            if file_name.lower().endswith('filter.m'):
                filter_name, _ = splitext(file_name)
                filters[filter_name] = join(root_path, filter_name)
    return filters

def get_sources(filter_dict, suffix="m"):
    return ["%s.%s" % (filter_pth, suffix) for filter_pth in filter_dict.values()]

def write_filter_header(filter_dict):
    headers = get_sources(filter_dict, suffix="h")
    with open("filters.h", 'wb') as header_fh:
        header_fh.write('''#import "filters/FilterBase.h"\n''')
        header_fh.writelines(['''#import "%s"\n''' % header for header in headers])

filters = find_filters()
sources = ['module.m', 'filters/FilterBase.m']
sources.extend(get_sources(filters))

print('Building tensorlib with %d filters:' % len(filters))
pprint(sorted(filters.keys()))

tensorlib = Extension('tensorlib',
    sources=sources,
    extra_compile_args=[
        '-Wno-error=unused-command-line-argument-hard-error-in-future',
        '-Wno-unused-function',
        '-Qunused-arguments',
        '-F%s' % frameworks],
    extra_link_args=[
        '-Wno-error=unused-command-line-argument-hard-error-in-future',
        '-L%s' % gpuimage_libs,
        '-F%s' % frameworks,
        '-framework', 'AppKit',
        '-framework', 'Foundation',
        '-framework', 'GPUImage'])

setup(name="tensorlib",
       version="1.0",
       author="fish2k",
       description="GPU-based image processing",
       ext_modules=[tensorlib],
       include_dirs=[gpuimage_headers])