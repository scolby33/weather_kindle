#!/bin/sh
# Emulate the update_weather.sh script, but only going as far as to generate the
# SVG and using relative directories to the source root. Useful for debugging
# during development.
set -x

BASE_DIR=src/weather

BIN_DIR="$BASE_DIR/bin"
CONFIG_DIR="$BASE_DIR/etc"
STATIC_DIR="$BASE_DIR/usr/share/weather"
CACHE_DIR="$BASE_DIR/var/cache/weather"

DOWNLOAD_WEATHER="$BIN_DIR/download_weather.py"

TEMPLATE="$STATIC_DIR/weather_template.svg"

. $CONFIG_DIR/weather_config.sh

mv "$CACHE_DIR/weather_out.svg" "$CACHE_DIR/weather_out.svg.old"
mv "$CACHE_DIR/weather_out.png" "$CACHE_DIR/weather_out.png.old"
mv "$CACHE_DIR/weather.png" "$CACHE_DIR/weather.png.old"

"$DOWNLOAD_WEATHER" ${ROTATED:+"--rotated"} ${METRIC:+"--metric"} --template ${TEMPLATE:?"missing TEMPLATE"} ${KEY:+"--key"} ${KEY:+"$KEY"} -- ${ZIP:+"$ZIP"} ${LAT:+"$LAT"} ${LON:+"$LON"} ${LOCATION:+"$LOCATION"} ${CITY_ID:+"$CITY_ID"} > "$CACHE_DIR/weather_out.svg"

