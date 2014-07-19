#!/usr/bin/python
# encoding: utf-8

print "Loading PlotDevice.app environment..."

import plotdevice # adds pyobjc to sys.path as a side effect...
import objc # ...otherwise this would fail
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
from plotdevice.gui import ScriptController
from plotdevice.util import rsrc_path
from plotdevice.run import encoding
