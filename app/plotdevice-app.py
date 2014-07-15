
import sys
from os.path import isdir

# if there's a python in /usr/local, it's probably homebrew -- let's use it!
local_packages = '/usr/local/lib/python2.7/site-packages'
if isdir(local_packages):
    sys.path.append(local_packages)

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
