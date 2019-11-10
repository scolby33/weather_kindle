#!/bin/sh

[ -f ./libotautils ] && . ./libotautils

HACKNAME="weather"
HACKVER="1.0.0"

LOGCOMPONENT="install"

# Directories
WEATHER_BASEDIR="/mnt/us/$HACKNAME"
EXTENSIONS_BASEDIR="/mnt/us/extensions/$HACKNAME"

# Files
WEATHER_CONFIG="$WEATHER_BASEDIR/etc/weather_config.sh"
WEATHER_CONFIG_BU="$WEATHER_BASEDIR/../weather_config.sh.orig"

# remove existing install, preserving config
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Removing existing weather install."
if [ -f "$WEATHER_CONFIG" ]; then
    logmsg "I" "$LOGCOMPONENT" "" "Found existing config; preserving it."
    cp "$WEATHER_CONFIG" "$WEATHER_CONFIG_BU"
fi
rm -rf "$WEATHER_BASEDIR"

# install new version
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Unpacking weather to user store."
# Make sure xzdec is executable first
chmod +x xzdec; ./xzdec "$HACKNAME.tar.xz" | tar -xvf - -C /mnt/us
_RET=$?
if [ "$_RET" -ne 0 ]; then
    logmsg "C" "$LOGCOMPONENT" "code=$_RET" "Failed to unpack weather."
    exit 1
fi
# backup default config
cp -f "$WEATHER_CONFIG" "$WEATHER_CONFIG.default"

# replace config if necessary
otautils_update_progressbar
if [ -f "$WEATHER_CONFIG_BU" ]; then
    logmsg "I" "$LOGCOMPONENT" "" "Restoring original config."
    mv "$WEATHER_CONFIG_BU" "$WEATHER_CONFIG"
fi

# compile Python bytecode
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Compiling Python bytecode for faster startup."
python3 -m compileall "$WEATHER_BASEDIR"

# make sure everything needed is executable
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Marking executables as executable."
chmod -R +x "$WEATHER_BASEDIR/bin" "$EXTENSIONS_BASEDIR/bin"

# clean up
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Cleaning up."
rm -f "$HACKNAME.tar.xz" "xzdec"

# sync the filesystem
otautils_update_progressbar
sync

# done
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Done!"

otautils_update_progressbar
return 0

