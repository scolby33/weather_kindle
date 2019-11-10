#!/bin/sh

_FUNCTIONS=/etc/rc.d/functions
[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}

EIPS_MAXLINES=$((SCREEN_Y_RES / EIPS_Y_RES))

INIT_WEATHER="/mnt/us/weather/bin/init_weather.sh"

CRONTAB="/etc/crontab/root"
CRONTAB_SIGIL="__WEATHER_AUTO__"
CRONTAB_LINE="0 * * * * /mnt/us/weather/bin/update_weather.sh  # update the weather display at the top of every hour $CRONTAB_SIGIL"


_msg() {
    # print a message one line from the bottom of the screen
    eips 0 $((EIPS_MAXLINES - 2)) "$1" > /dev/null
}

_installed() {
    # check if we're installed in the crontab
    # returns 0 if installed, 1 if not installed
    grep -q "$CRONTAB_SIGIL" "$CRONTAB"
}

status() {
    # print crontab installation status to the screen
    if _installed; then
        _msg "  Crontab installed."
    else
        _msg "  Crontab not installed."
    fi
}

install() {
    # add line to crontab if not already present
    if ! _installed; then
        mntroot rw
        echo "$CRONTAB_LINE" >> "$CRONTAB"
        mntroot ro
    fi

    if _installed; then
        _msg "  Crontab successfully installed."
    else
        _msg "  Failed to install to crontab!"
        exit 1
    fi
}

uninstall() {
    # remove line from crontab
    mntroot rw
    sed -i "/$CRONTAB_SIGIL$/d" "$CRONTAB"
    mntroot ro

    if ! _installed; then
        _msg "  Crontab successfully uninstalled."
    else
        _msg "  Failed to uninstall crontab!"
        exit 1
    fi
}

start() {
    # enter weather display mode
    "$INIT_WEATHER"
}


## Main
case "${1}" in
"status")
    "${1}"
    ;;
"install")
    "${1}"
    ;;
"uninstall")
    "${1}"
    ;;
"start")
    "${1}"
    ;;
esac

