#!/bin/sh

[ -f ./libotautils ] && . ./libotautils

HACKNAME="weather"

LOGCOMPONENT="uninstall"

CRONTAB="/etc/crontab/root"
CRONTAB_SIGIL="__WEATHER_AUTO__"

# Directories
WEATHER_BASEDIR="/mnt/us/$HACKNAME"
EXTENSIONS_BASEDIR="/mnt/us/extensions/$HACKNAME"

# Files
WEATHER_CONFIG_BU="$WEATHER_BASEDIR/../weather_config.sh.orig"

# remove weather files in user store
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Removing weather files in user store."
rm -rf "$WEATHER_BASEDIR" "$WEATHER_CONFIG_BU"

# remove KUAL extension
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Removing KUAL extension."
rm -rf "$EXTENSIONS_BASEDIR"

# remove from crontab
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Removing weather from crontab if present."
if grep -q "$CRONTAB_SIGIL" "$CRONTAB"; then
    mntroot rw
    sed -i "/$CRONTAB_SIGIL$/d" "$CRONTAB"
    mntroot ro
fi

# sync the filesystem
otautils_update_progressbar
sync

# done
otautils_update_progressbar
logmsg "I" "$LOGCOMPONENT" "" "Done!"

otautils_update_progressbar
return 0

