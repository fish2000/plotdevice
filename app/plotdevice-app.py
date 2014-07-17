
import sys
from os import environ as env
from os.path import isdir, join

# if there's a python in /usr/local, it's probably homebrew -- let's use it!
local_packages = '/usr/local/lib/python2.7/site-packages'
if isdir(local_packages):
    sys.path.append(local_packages)

# If running from a py2app build, update sys.path
# with the bundle-local python package directory
RESOURCEPATH = env.get('RESOURCEPATH')
if RESOURCEPATH:
    sys.path.insert(0,
        join(RESOURCEPATH, 'python'))
    sys.path.insert(0,
        join(RESOURCEPATH, 'python', 'PyObjC'))

# remove dupes from sys.path -- for an explanation see:
# http://stackoverflow.com/a/480227/298171
seen = set()
seen_add = seen.add
clean_path = tuple(directory for directory in sys.path \
    if directory not in seen and \
        not seen_add(directory))
sys.path = list(clean_path)

# install a signal handler to quit on ^c (should the app ever be launched from terminal)
import objc
import AppKit
from signal import signal, SIGINT
signal(SIGINT, lambda m, n: AppKit.NSApplication.sharedApplication().terminate_(True))

# PlotDevice is a typical document-based application. We'll import the PlotDeviceDocument
# class et al from the gui module and the corresponding document-type defined in the
# info.plist will do the rest.
import plotdevice.gui

# loop forever
from PyObjCTools import AppHelper
AppHelper.runEventLoop()
