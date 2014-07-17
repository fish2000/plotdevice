#!/usr/bin/env python
# encoding: utf-8

import plotdevice # adds pyobjc to sys.path as a side effect...
import objc # ...otherwise this would fail
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
from plotdevice.gui import ScriptController
from plotdevice.util import rsrc_path
from plotdevice.run import encoding
