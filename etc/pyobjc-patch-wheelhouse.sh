#!/usr/bin/env bash

PRAXA_DOWNLOAD_CACHE="cache/downloads"
WHEELHOUSE="${PWD}/cache/wheelhouse"
mkdir -p $PRAXA_DOWNLOAD_CACHE
mkdir -p $WHEELHOUSE
mkdir -p build

source "etc/download.sh"
source "etc/urlcache.sh"

PYOBJC_VERSION="2.5.1"
PYOBJC_DOWNLOAD_URL="https://bitbucket.org/ronaldoussoren/pyobjc/get/pyobjc-${PYOBJC_VERSION}.zip"
PYOBJC_BUILD_PATH="build/pyobjc-${PYOBJC_VERSION}"
PYOBJC_VIRTUALENV="build/pyobjc-virtualenv-${PYOBJC_VERSION}"

rm -rf $PYOBJC_BUILD_PATH $PYOBJC_VIRTUALENV
fetch_and_expand $PYOBJC_DOWNLOAD_URL $PYOBJC_BUILD_PATH

declare -a names=("AppleScriptKit" \
"Accounts" \
"AddressBook" \
"AppleScriptKit" \
"AppleScriptObjC" \
"Automator" \
"CFNetwork" \
"CalendarStore" \
"Cocoa" \
"Collaboration" \
"CoreData" \
"CoreLocation" \
"CoreText" \
#"CoreWLAN" \
"DictionaryServices" \
#"DiskArbitration" \
"EventKit" \
"ExceptionHandling" \
"FSEvents" \
"InputMethodKit" \
"InstallerPlugins" \
"InstantMessage" \
#"InterfaceBuilderKit" \
"LatentSemanticMapping" \
"LaunchServices" \
#"Message" \
"OpenDirectory" \
"PreferencePanes" \
"PubSub" \
"QTKit" \
"Quartz" \
"ScreenSaver" \
"ScriptingBridge" \
"SearchKit" \
"ServerNotification" \
"ServiceManagement" \
"Social" \
#"StoreKit" \
"SyncServices" \
"SystemConfiguration" \
"WebKit")
#"XgridFoundation")

PYOBJC_DIR=$PWD/$PYOBJC_BUILD_PATH
FIND="for fn in install_lib._install_lib.get_outputs(self):"
REPLACE="for fn, _ in result.items():"

########## FIX SETUPS ######################################################################

cd $PYOBJC_DIR/pyobjc-core && sed -i \~ -e "s#${FIND}#${REPLACE}#" distribute_setup.py
cd $PYOBJC_DIR/pyobjc-core && sed -i \~ -e "s#${FIND}#${REPLACE}#" setup.py
cd $PYOBJC_DIR/pyobjc && sed -i \~ -e "s#${FIND}#${REPLACE}#" distribute_setup.py
cd $PYOBJC_DIR/pyobjc && sed -i \~ -e "s#${FIND}#${REPLACE}#" setup.py

for name in "${names[@]}"; do
    cd $PYOBJC_DIR && \
    cd "pyobjc-framework-${name}" && \
    sed -i \~ -e "s#${FIND}#${REPLACE}#" *setup.py
done

find $PYOBJC_DIR -name \*.py~ -print -delete

########## LOCAL INSTALL ###################################################################

virtualenv -v -p `which python` $PYOBJC_VIRTUALENV
source $PYOBJC_VIRTUALENV/bin/activate

cd $PYOBJC_DIR/pyobjc-core && pip install --verbose --no-deps .
cd $PYOBJC_DIR/pyobjc && pip install --verbose .

########## WHEELHOUSE ######################################################################

pip install -U wheel

cd $PYOBJC_DIR/pyobjc-core && pip wheel --verbose --no-deps -w $WHEELHOUSE .
cd $PYOBJC_DIR/pyobjc && pip wheel --verbose --no-deps -w $WHEELHOUSE .

for name in "${names[@]}"; do
    cd $PYOBJC_DIR && \
    cd "pyobjc-framework-${name}" && \
    pip wheel --verbose --no-deps -w $WHEELHOUSE .
done
