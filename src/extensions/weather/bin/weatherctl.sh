#!/bin/sh

HACKNAME="${PWD##/mnt/us/extensions/}"

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

MY_SCREEN_SIZE="${SCREEN_X_RES}x${SCREEN_Y_RES}"
EIPS_MAXCHARS="$((${SCREEN_X_RES} / ${EIPS_X_RES}))"
EIPS_MAXLINES="$((${SCREEN_Y_RES} / ${EIPS_Y_RES}))"


install() {
    if status
    then
        mntroot rw
        echo "0 * * * * /mnt/us/weather/bin/update_weather.sh # update the weather display at the top of every hour" >> /etc/crontab/root
        mntroot ro
    fi
}

uninstall() {
    mntroot rw
    sed "\_^0 \* \* \* \* /mnt/us/weather/bin/update_weather.sh # update the weather display at the top of every hour$_d" /etc/crontab/root > /etc/crontab/root
    mntroot ro
}

_status() {
    grep -q "^0 * * * * /mnt/us/weather/bin/update_weather.sh # update the weather display at the top of every hour$" /etc/crontab/root
    return $?
}

status() {
    if _status
    then
        eips 0 $((${EIPS_MAXLINES} - 2)) "  Crontab installed" > /dev/null
    else
        eips 0 $((${EIPS_MAXLINES} - 2)) "  Crontab not installed" > /dev/null
    fi  
}

start() {
    /mnt/us/${HACKNAME}/bin/init_weather.sh
}


## Main
case "${1}" in
"install")
    ${1}
    ;;
"uninstall")
    ${1}
    ;;
"status")
    ${1}
    ;;
"start")
    ${1}
    ;;
esac
