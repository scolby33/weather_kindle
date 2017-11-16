#!/bin/sh

[ -f ./libotautils ] && source ./libotautils

HACKNAME="weather"

otautils_update_progressbar
# Remove existing install
logmsg "I" "install" "" "removing existing weather install..."
if [ -d "/mnt/us/weather" ]; then
    rm -rf "/mnt/us/weather"
fi

otautils_update_progressbar
# Install Weather in the userstore
logmsg "I" "install" "" "unpacking weather..."
# Make sure xzdec is executable first
chmod +x ./xzdec
./xzdec "${HACKNAME}.tar.xz" | tar -xvf - -C /mnt/us/
_RET=$?
if [ ${_RET} -ne 0 ]; then
    logmsg "C" "install" "code=${_RET}" "failed to update userstore with custom directory"
    echo "${_RET}" >> $WLOG
    return 1
fi

otautils_update_progressbar
# Backup default config
cp -f /mnt/us/weather/etc/weather_config /mnt/us/weather/etc/weather_config.default

otautils_update_progressbar
logmsg "I" "install" "" "cleaning up"
rm -f "${HACKNAME}.tar.xz" "xzdec"

otautils_update_progressbar
logmsg "I" "install" "" "done"

otautils_update_progressbar
return 0
