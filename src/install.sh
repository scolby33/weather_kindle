#!/bin/sh

[ -f ./libotautils ] && . ./libotautils

HACKNAME="weather"
HACKVER="1.0.0"

# Directories
WEATHER_BASEDIR="/mnt/us/$HACKNAME"
EXTENSIONS_BASEDIR="/mnt/us/extensions/$HACKNAME"

# Files
WEATHER_CONFIG="$WEATHER_BASEDIR/etc/weather_config.sh"
WEATHER_CONFIG_BU="$WEATHER_BASEDIR/../weather_config.sh.orig"

# remove existing install, preserving config
otautils_update_progressbar
logmsg "I" "install" "" "Removing existing weather install"
if [ -f "$WEATHER_CONFIG" ]; then
    logmsg "I" "install" "" "Found existing config; preserving it"
    cp "$WEATHER_CONFIG" "$WEATHER_CONFIG_BU"
fi
rm -rf "$WEATHER_BASEDIR"

# install new version
otautils_update_progressbar
logmsg "I" "install" "" "Unpacking weather to user store"
# Make sure xzdec is executable first
chmod +x xzdec; ./xzdec "$HACKNAME.tar.xz" | tar -xvf - -C /mnt/us
_RET=$?
if [ "$_RET" -ne 0 ]; then
    logmsg "C" "install" "code=$_RET" "Failed to unpack weather."
    exit 1
fi
# backup default config
cp -f "$WEATHER_CONFIG" "$WEATHER_CONFIG.default"

# replace config if necessary
otautils_update_progressbar
if [ -f "$WEATHER_CONFIG_BU" ]; then
    logmsg "I" "install" "" "Restoring original config"
    mv "$WEATHER_CONFIG_BU" "$WEATHER_CONFIG"
fi

# make sure everything needed is executable
otautils_update_progressbar
logmsg "I" "install" "" "Marking executables as executable"
chmod -R +x "$WEATHER_BASEDIR/bin" "$EXTENSIONS_BASEDIR/bin"

# clean up
otautils_update_progressbar
logmsg "I" "install" "" "Cleaning up"
rm -f "$HACKNAME.tar.xz" "xzdec"

# done
otautils_update_progressbar
logmsg "I" "install" "" "Done!"

otautils_update_progressbar
return 0

