#!/bin/sh

cd /mnt/us/weather || exit 1

BIN_DIR=bin
CONFIG_DIR=etc
STATIC_DIR=usr/share/weather
CACHE_DIR=var/cache/weather

DOWNLOAD_WEATHER="$BIN_DIR/download_weather.py"
RSVG_CONVERT="$BIN_DIR/rsvg-convert"
PNGCRUSH="$BIN_DIR/pngcrush"
EIPS="/usr/sbin/eips"

TEMPLATE="$STATIC_DIR/weather_template.svg"

# shellcheck source=../etc/weather_config.sh
. "$CONFIG_DIR/weather_config.sh"

# save current images as old; mostly useful for debugging
mv "$CACHE_DIR/weather_out.svg" "$CACHE_DIR/weather_out.svg.old"
mv "$CACHE_DIR/weather_out.png" "$CACHE_DIR/weather_out.png.old"
mv "$CACHE_DIR/weather.png" "$CACHE_DIR/weather.png.old"

"$DOWNLOAD_WEATHER" ${ROTATED:+"--rotated"} ${METRIC:+"--metric"} --template ${TEMPLATE:?"missing TEMPLATE"} ${KEY:+"--key"} ${KEY:+"$KEY"} -- ${ZIP:+"$ZIP"} ${LAT:+"$LAT"} ${LON:+"$LON"} ${LOCATION:+"$LOCATION"} > "$CACHE_DIR/weather_out.svg"

# convert the svg to a png with white background (no transparency allowed!)
"$RSVG_CONVERT" --background-color=white -o "$CACHE_DIR/weather_out.png" "$CACHE_DIR/weather_out.svg"

# change png to greyscale without alpha (color type (-c) 0)
"$PNGCRUSH" -qf -c 0 "$CACHE_DIR/weather_out.png" "$CACHE_DIR/weather.png"

# clear the screen twice to prevent ghosting
"$EIPS" -c
"$EIPS" -c

# if everything worked, put the weather up; if not, show an error
if [ -e "$CACHE_DIR/weather.png" ]; then
    "$EIPS" -g "$CACHE_DIR/weather.png"
    exit $?
else
    "$EIPS" -g "$STATIC_DIR/error${ROTATED+_rotated}.png"
    _RET=$?
    if [ "$_RET" -ne 0 ]; then
        exit "$_RET"
    else
        exit 1
    fi
fi
