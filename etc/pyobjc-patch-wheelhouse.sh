#!/usr/bin/env bash

PRAXA_DOWNLOAD_CACHE="cache/downloads"
WHEELHOUSE="${PWD}/cache/wheelhouse"
mkdir -p $PRAXA_DOWNLOAD_CACHE
mkdir -p $WHEELHOUSE

source "etc/download.sh"
source "etc/urlcache.sh"

PYOBJC_VERSION="2.5.1"
PYOBJC_DOWNLOAD_URL="https://bitbucket.org/ronaldoussoren/pyobjc/get/pyobjc-${PYOBJC_VERSION}.zip"
PYOBJC_BUILD_PATH="build/pyobjc-${PYOBJC_VERSION}"

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

########## FIX SETUPS ##########
for name in "${names[@]}"; do
    cd $PYOBJC_DIR && \
    cd "pyobjc-framework-${name}" && \
    sed -i \~ -e "s#${FIND}#${REPLACE}#" pyobjc_setup.py
done

#cd $PYOBJC_DIR/pyobjc-core && sed -i \~ -e "s#${FIND}#${REPLACE}#" distribute_setup.py
cd $PYOBJC_DIR/pyobjc-core && sed -i \~ -e "s#${FIND}#${REPLACE}#" setup.py
#cd $PYOBJC_DIR/pyobjc && sed -i \~ -e "s#${FIND}#${REPLACE}#" distribute_setup.py
#cd $PYOBJC_DIR/pyobjc && sed -i \~ -e "s#${FIND}#${REPLACE}#" setup.py

find $PYOBJC_DIR -name \*.py~ -print -delete

########## WHEELHOUSE ##########
#mkdir -p $WHEELHOUSE

for name in "${names[@]}"; do
    cd $PYOBJC_DIR && \
    cd "pyobjc-framework-${name}" && \
    pip wheel --verbose --no-deps -w $WHEELHOUSE .
done

cd $PYOBJC_DIR/pyobjc-core && pip wheel --verbose --no-deps -w $WHEELHOUSE .
cd $PYOBJC_DIR/pyobjc && pip wheel --verbose --no-deps -w $WHEELHOUSE .
