# encoding:utf-8

# This is your standard setup.py, so to install the module & command line tool, use:
#     python setup.py install
#
# In addition to the `install' command, there are a few other variants:
#
#    app:    builds ./dist/PlotDevice.app using Xcode
#    py2app: builds the application using py2app
#    clean:  discard anything already built and start fresh
#    build:  puts the module in a usable state. after building, you should be able
#            to run the ./app/plotdevice command line tool within the source distribution.
#            If you're having trouble building the app, this can be a good way to sanity
#            check your setup
#
# We require some dependencies:
# - Mac OS X 10.9+
# - py2app or xcode or just pip
# - PyObjC (should be in /System/Library/Frameworks/Python.framework/Versions/2.7/Extras)
# - cPathMatics, cGeo, cIO, cEvent, & polymagic (included in the "app/deps" folder)
# - Sparkle.framework (auto-downloaded only for `dist` builds)

import sys, os, urllib2, plistlib
from distutils.dir_util import remove_tree
from distutils.spawn import find_executable as which
from distutils.core import Command
from setuptools.command.sdist import sdist
from distutils.command.build_py import build_py
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound
from os import listdir, getcwd
from os.path import join, exists, isdir, dirname, basename, abspath, getsize

## Metadata ##
__version__ = '0.9.2'
__author__  = 'Christian Swinehart'
__email__   = "drafting@samizdat.cc"
__credits__ = 'Frederik De Bleser, Tom De Smedt, Just van Rossum, & Marcos Ojeda'
__license__ = 'MIT'

# PyPI fields
APP_NAME = 'PlotDevice'
MODULE = APP_NAME.lower()
VERSION = __version__
AUTHOR = __author__
AUTHOR_EMAIL = __email__
LICENSE = __license__
URL = "http://plotdevice.io/"
CLASSIFIERS = (
    "Development Status :: 5 - Production/Stable",
    "Environment :: MacOS X :: Cocoa",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Programming Language :: Python",
    "Topic :: Artistic Software",
    "Topic :: Multimedia :: Graphics",
    "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
    "Topic :: Multimedia :: Video",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: Text Editors :: Integrated Development Environments (IDE)",
)
DESCRIPTION = "Create 2-dimensional graphics and animation using Python code"
LONG_DESCRIPTION = """PlotDevice is a Macintosh application used in graphic design research. It provides an
interactive Python environment where you can create two-dimensional graphics
and output them in a variety of vector, bitmap, and animation formats. It is
meant both as a sketch environment for exploring generative design and as a
general purpose graphics library for use in stand-alone Python programs.

PlotDevice is a fork of NodeBox 1.9.7rc1 with support for modern versions of
Python and Mac OS.

The new version features:
* Enhanced command line interface.
* New text editor with tab completion, syntax color themes, and emacs/vi bindings.
* Video export in H.264 or animated gif formats (with [GCD](http://en.wikipedia.org/wiki/Grand_Central_Dispatch)-based i/o).
* Added support for external editors by reloading the source when changed.
* Build system now works with Xcode or `py2app` for the application and `pip` for the module.
* Virtualenv support (for both installation of the module and running scripts with dependencies).
* External scripts can use `from plotdevice.script import *` to create a drawing environment.
* Simplified bezier & affine transform api using the python ‘with’ statement
* Now uses the system's Python 2.7 interpreter.

Requires:
* Mac OS X 10.9+
"""


## Basic Utils ##

# the sparkle updater framework will be fetched as needed
SPARKLE_VERSION = '1.7.0'
SPARKLE_URL = 'https://github.com/pornel/Sparkle/releases/download/%(v)s/Sparkle-%(v)s.tar.bz2'% { 'v': SPARKLE_VERSION }

# helpers for dealing with plists & git (spiritual cousins if ever there were)
def info_plist(pth='app/PlotDevice-Info.plist'):
    info = plistlib.readPlist(pth)
    # overwrite the xcode placeholder vars
    info['CFBundleExecutable'] = info['CFBundleName'] = APP_NAME
    return info

def update_plist(pth, **modifications):
    info = plistlib.readPlist(pth)
    for key, val in modifications.items():
        if val is None:
            info.pop(key)
        else:
            info[key] = val
    plistlib.writePlist(info, pth)

def last_commit():
    commit_count, _, _ = gosub('git log --oneline | wc -l')
    return 'r%s' % commit_count.strip()

def commits_since(rev, raw=False):
    log, _, _ = gosub('git log --oneline')
    commits = log.decode('utf-8').splitlines()
    since = int(rev.replace('r',''))
    recent = [c.split(' ',1)[1] for c in commits[:-since]]
    if not raw:
        return u'\n<li>%s</li>\n'%u'</li>\n<li>'.join(recent)
    return recent

# basicaly `backticks`
def gosub(cmd, on_err=True):
    """Run a shell command and return the output"""
    from subprocess import Popen, PIPE
    shell = isinstance(cmd, basestring)
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=shell)
    out, err = proc.communicate()
    ret = proc.returncode
    if on_err:
        msg = '%s:\n' % on_err if isinstance(on_err, basestring) else ''
        assert ret==0, msg + (err or out)
    return out, err, ret

## Distribution Build Utils ##

def timestamp():
    from datetime import datetime
    from pytz import timezone, utc
    now = utc.localize(datetime.utcnow()).astimezone(timezone('US/Eastern'))
    return now.strftime("%a, %d %b %Y %H:%M:%S %z")

def last_release():
    from xml.etree.ElementTree import fromstring
    feed_xml = urllib2.urlopen('http://plotdevice.io/app.xml').read().decode('utf-8')
    for item in fromstring(feed_xml.encode('utf-8')).iter('revision'):
        return item.text
    return 'r0'

def merged_feed(new_release):
    # fetch the current app feed
    feed_xml = urllib2.urlopen('http://plotdevice.io/app.xml').read().decode('utf-8')

    # collect the commit logs since the previous post
    new_release['commits'] = commits_since(last_release())

    # yes, this is totally caveman parsing, but xml.etree doesn't support cdata blocks...
    spliced = []
    item_tmpl = u"""<item>
      <title>Version %(version)s</title>
      <revision>%(revision)s</revision>
      <pubDate>%(now)s</pubDate>
      <sparkle:minimumSystemVersion>10.9</sparkle:minimumSystemVersion>
      <description><![CDATA[
        <h2>Recent changes</h2>
        <ul>%(commits)s</ul>
      ]]></description>
      <enclosure url="http://plotdevice.io/app/%(zipfile)s" sparkle:shortVersionString="%(version)s" sparkle:version="%(revision)s" length="%(bytes)s" type="application/octet-stream" />
    </item>"""
    item_xml = item_tmpl%new_release
    for line in feed_xml.splitlines():
        if '<item>' in line and item_xml:
            spliced.append(u' '*4 + item_xml)
            item_xml = None
        spliced.append(line)
    return (u"\n".join(spliced)).encode('utf-8')

## Build Commands ##

class CleanCommand(Command):
    description = "wipe out the ./build ./dist and app/deps/.../build dirs"
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        os.system('find . -iname .ds_store -print -delete')
        os.system('find . -name \*.pyc -print -delete')
        os.system('rm -rf ./build ./dist')
        os.system('rm -rf ./Xcode/Build ./Xcode/Intermediates ./DerivedData')
        os.system('rm -rf ./app/deps/*/build')
        os.system('rm -rf plotdevice.egg-info MANIFEST.in PKG')

class WheelhouseCache(Command):
    description = "Cache wheels and wheel source"
    user_options = [
        ('clean', 'C', 'Clean wheelhouse and download cache')]
    
    def initialize_options(self):
        self.clean = False
    
    def finalize_options(self):
        self.clean = bool(self.clean)
    
    def run(self):
        CACHE = join(getcwd(), 'cache')
        CACHE_SCRIPT = join(getcwd(), 'etc', 'load-cache.sh')
        if self.clean:
            remove_tree(CACHE)
            return
        self.spawn([CACHE_SCRIPT])

class WheelhouseToApp(Command):
    description = "Install PlotDevice.app requirements from the wheelhouse"
    user_options = [
        ('wheelhouse=', 'w', 'Wheelhouse directory [default: cache/wheelhouse/]'),
        ('app=', 'a', 'App bundle directory [default: dist/PlotDevice.app/]')]
    
    def initialize_options(self):
        self.wheelhouse = 'cache/wheelhouse/'
        self.app = 'dist/PlotDevice.app'
    
    def finalize_options(self):
        self.wheelhouse = abspath(self.wheelhouse)
        self.app = abspath(self.app)
    
    def run(self):
        ''' try to install wheels to app bundle '''
        if self.install_wheels():
            print "Done installing wheels"
    
    def install_wheels(self):
        ''' Install everything from the wheelhouse '''
        try:
            from wheel.install import WheelFile
        except ImportError:
            print "ERROR: install the `wheel` Python package to enable bundle-local PyObjC"
            return False
        
        WHEELHOUSE = self.wheelhouse
        APP = self.app
        DITTO = which('ditto')
        
        if not isdir(WHEELHOUSE):
            print "ERROR: no wheelhouse directory at %s" % WHEELHOUSE
            return False
        
        WHEELS = filter(
            lambda wheel_file: wheel_file.lower().endswith('.whl'),
            listdir(WHEELHOUSE))
        PYOBJC_WHEELS = filter(
            lambda wheel_file: wheel_file.lower().startswith('pyobjc'),
            WHEELS)
        OTHER_WHEELS = sorted(list(
            set(WHEELS) - set(PYOBJC_WHEELS)))
        
        CONTENTS = join(APP, 'Contents')
        RESOURCES = join(CONTENTS, 'Resources')
        SITE_PACKAGES = join(RESOURCES, 'python')
        HEADERS = join(CONTENTS, 'PrivateHeaders')
        SCRIPTS = join(CONTENTS, 'SharedSupport')
        OVERRIDES = dict(
            purelib=SITE_PACKAGES, platlib=SITE_PACKAGES, data=SITE_PACKAGES,
            headers=HEADERS, scripts=SCRIPTS)
        
        self.mkpath(HEADERS)
        
        for pyobjc_wheel_file in sorted(PYOBJC_WHEELS):
            print "+ Installing PyObjC wheel: %s" % pyobjc_wheel_file
            wheel = WheelFile(join(WHEELHOUSE, pyobjc_wheel_file))
            wheel.install(overrides=OVERRIDES, force=True)
        
        for wheel_file in sorted(OTHER_WHEELS):
            print "+ Installing wheel: %s" % wheel_file
            wheel = WheelFile(join(WHEELHOUSE, wheel_file))
            wheel.install(overrides=OVERRIDES, force=True)
        
        # misc. PyObjC patching (ideally should obvi be fixed in the upstream repository)
        self.spawn([DITTO,
            join(SITE_PACKAGES, 'PyObjCTools'),
            join(SITE_PACKAGES, 'PyObjC', 'PyObjCTools')])
        self.spawn(['touch',
            join(SITE_PACKAGES, 'PyObjC', 'PyObjCTools', '__init__.py')])
        
        return True

class BuildDistCommand(sdist):
    def finalize_options(self):
        with file('MANIFEST.in','w') as f:
            tracked, _, _ = gosub('git ls-tree --full-tree --name-only -r HEAD')
            for line in tracked.splitlines()[1:]:
                f.write("include %s\n"%line)
        sdist.finalize_options(self)

    def run(self):
        sdist.run(self)

        # it would be nice to clean up MANIFEST.in and plotdevice.egg-info here,
        # but we'll see if the upload command depends on them...
        remove_tree('plotdevice.egg-info')
        os.unlink('MANIFEST.in')

class BuildCommand(build_py):
    def run(self):
        # first let the real build_py routine do its thing
        build_py.run(self)

        # then compile the extensions into the just-built module
        self.spawn([which('python'), 'app/deps/build.py', abspath(self.build_lib)])

        # include some ui resources for running a script from the command line
        rsrc_dir = '%s/plotdevice/rsrc' % self.build_lib
        self.mkpath(rsrc_dir)
        self.copy_file("app/Resources/colors.json", '%s/colors.json' % rsrc_dir)
        self.spawn([which('ibtool'), '--compile',
            '%s/viewer.nib' % rsrc_dir,
            "app/Resources/English.lproj/PlotDeviceScript.xib"])
        self.copy_file("app/Resources/PlotDeviceFile.icns", '%s/viewer.icns' % rsrc_dir)

class BuildAppCommand(Command):
    description = "Build PlotDevice.app with xcode"
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        self.spawn(['xcodebuild'])
        remove_tree('dist/PlotDevice.app.dSYM')
        print "done building PlotDevice.app in ./dist"

try:
    from py2app.build_app import py2app as build_py2app
    class BuildPy2AppCommand(build_py2app):
        description = """Build PlotDevice.app with py2app (then undo some of its questionable layout defaults)"""
        def initialize_options(self):
            build_py2app.initialize_options(self)
        def finalize_options(self):
            self.verbose=0
            build_py2app.finalize_options(self)
        
        sub_commands = build_py2app.sub_commands[:]
        sub_commands.append(('wheelhouse', lambda arg: True))
        
        def run(self):
            build_py2app.run(self)
            if self.dry_run:
                return

            # undo py2app's weird treatment of the config.version value
            info_pth = 'dist/PlotDevice.app/Contents/Info.plist'
            update_plist(info_pth, CFBundleShortVersionString=None)

            # set up internal paths and ensure destination dirs exist
            RSRC = self.resdir
            CONTENTS = dirname(RSRC)
            BIN = join(CONTENTS, 'SharedSupport')
            MODULE = join(self.bdist_base, 'lib', 'plotdevice')
            PY = join(RSRC, 'python')
            PLOTDEVICE = join(PY, 'plotdevice')
            DITTO = which('ditto')

            for pth in BIN, PY:
                self.mkpath(pth)

            # install the module in Resources/python
            self.spawn([DITTO, MODULE, PLOTDEVICE])

            # discard the eggery-pokery
            remove_tree(join(RSRC, 'lib'), dry_run=self.dry_run)
            os.unlink(join(RSRC, 'include'))
            os.unlink(join(RSRC, 'site.pyc'))

            # place the command line tools in SharedSupport
            self.copy_file("app/plotdevice", BIN)
            self.copy_file("app/bplotdevice", BIN)

            for cmd in self.get_sub_commands():
                self.run_command(cmd)

            # success!
            print "done building PlotDevice.app in ./dist"

except DistributionNotFound:
    # virtualenv doesn't include pyobjc, py2app, etc. in the sys.path for some reason.
    # not being able to access py2app isn't a big deal for 'build', 'app', 'dist', or 'clean'
    # so only abort the build if the 'py2app' command was given
    if 'py2app' in sys.argv:
        print """setup.py: py2app build failed
          Couldn't find the py2app module (perhaps because you've called setup.py from a virtualenv).
          Make sure you're not in a virtualenv directory or shell, and that you're using either:
          
              * Apple's system-installed python: /usr/bin/python -- or,
              * A Homebrew python install: /usr/local/bin/python
              
          ... for py2app builds (The latter option should be a framework build). """
        sys.exit(1)


## Packaging Commands (really only useful to the maintainer) ##

class DistCommand(Command):
    description = "Create distributable zip of the app and an updated app.xml feed"
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    sub_commands = Command.sub_commands[:]
    sub_commands.append(('wheelhouse', lambda arg: True))
    def run(self):
        APP = 'dist/PlotDevice.app'
        ZIP = 'dist/PlotDevice_app-%s.zip' % VERSION

        # build the app
        self.spawn(['xcodebuild'])

        # we don't need no stinking core dumps
        remove_tree(APP+'.dSYM')

        # set the bundle version to the current commit number and prime the updater
        info_pth = 'dist/PlotDevice.app/Contents/Info.plist'
        update_plist(info_pth,
            CFBundleVersion = last_commit(),
            CFBundleShortVersionString = VERSION,
            SUFeedURL = 'http://plotdevice.io/app.xml',
            SUEnableSystemProfiling = 'YES')
        
        # Deal with installable frameworks:
        FRAMEWORKS = join('app', 'Frameworks')
        DITTO = which('ditto')
        self.mkpath(FRAMEWORKS)

        # Download Sparkle (if necessary) and copy it into the bundle
        ORIG = join(FRAMEWORKS, 'Sparkle-%s' % SPARKLE_VERSION, 'Sparkle.framework')
        SPARKLE = join(APP, 'Contents', 'Frameworks', 'Sparkle.framework')
        if not exists(ORIG):
            print "Downloading Sparkle.framework"
            os.system('%(curl)s -L %(url)s | %(bz)s -c | %(tar)s xf - -C %(fw)s' % dict(
                curl=which('curl'), url=SPARKLE_URL,
                bz=which('bunzip2'),
                tar=which('tar'), fw=FRAMEWORKS))
        self.mkpath(dirname(SPARKLE))
        self.spawn([DITTO, ORIG, SPARKLE])

        # code-sign the app and sparkle bundles, then verify
        self.spawn(['codesign', '-f', '-v', '-s', "Developer ID Application", SPARKLE])
        self.spawn(['codesign', '-f', '-v', '-s', "Developer ID Application", APP])
        self.spawn(['spctl', '--assess', '-v', 'dist/PlotDevice.app'])

        # create versioned zipfile of the app
        self.spawn([DITTO, '-ck', '--keepParent', APP, ZIP])

        # update the app.xml feed (pulled from the server)
        release = dict(zipfile=basename(ZIP), bytes=getsize(ZIP),
                       version=VERSION, revision=last_commit(), now=timestamp())
        with file('dist/app.xml','w') as f:
            f.write(merged_feed(release))

        for cmd in self.get_sub_commands():
            self.run_command(cmd)

        print "\nBuilt PlotDevice.app, %s, and app.xml in ./dist" % basename(ZIP)
        print " -" + "\n -".join(commits_since(last_release(), raw=True))
        print "now edit dist/app.xml then run `python setup.py submit`."


class SubmitCommand(Command):
    description = "Validate contents of dist subdir then send them to the net"
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        print "Checking feed xml"
        gosub('%s -xml -utf8 -e dist/app.xml' % which('tidy'),
            on_err="app.xml didn't validate properly")

        from xml.etree.ElementTree import parse
        zipfile = 'dist/PlotDevice_app-%s.zip' % VERSION
        SCP = which('scp')

        for item in parse('dist/app.xml').getroot().iter('item'):
            release = item.find('enclosure').attrib
            assert release['url'].endswith(basename(zipfile)), "Version mismatch: %s vs %r" % (
                zipfile, release['url'])
            break

        # <confirmation y.n goes here>

        print "posting dist/app.xml"
        gosub('%s dist/app.xml plotdevice.io:plod' % SCP)

        print "posting", zipfile
        gosub('%s %s plotdevice.io:plod/app' % (SCP, zipfile))

        # <upload to pypi goes here>

## Run Build ##

if __name__ == '__main__':
    # make sure we're at the project root regardless of the cwd
    # (this means the various commands don't have to play path games)
    os.chdir(dirname(abspath(__file__)))

    # common config between module and app builds
    config = dict(
        name=MODULE,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        classifiers=CLASSIFIERS,
        packages=find_packages(),
        scripts=[
            "app/plotdevice",
            "app/bplotdevice"],
        setup_requires=['wheel>=0.24.0'],
        zip_safe=False,
        cmdclass={
            'app': BuildAppCommand,
            'wheelcache': WheelhouseCache,
            'wheelhouse': WheelhouseToApp,
            'clean': CleanCommand,
            'build_py': BuildCommand,
            'dist': DistCommand,
            'sdist': BuildDistCommand,
            'submit': SubmitCommand,
        })

    # py2app-specific config 
    if 'py2app' in sys.argv:
        config.update(dict(
            app=[{
                'script': "app/plotdevice-app.py",
                "plist": info_plist(),
            }],
            data_files=[
                "app/Resources/ui",
                "app/Resources/English.lproj",
                "app/Resources/PlotDevice.icns",
                "app/Resources/PlotDeviceFile.icns",
                "examples",
            ],
            options={
                "py2app": {
                    "iconfile": "app/Resources/PlotDevice.icns",
                    "semi_standalone": True,
                    "site_packages": True,
                    "strip": False,
                }
            },
            cmdclass={
                'wheelcache': WheelhouseCache,
                'wheelhouse': WheelhouseToApp,
                'build_py': BuildCommand,
                'py2app': BuildPy2AppCommand,
            }))

    # begin the build process
    setup(**config)
