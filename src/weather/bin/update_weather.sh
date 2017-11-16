#!/bin/sh

cd /mnt/us/weather

source etc/weather_config

# clean up old images
rm img/weather_out.svg.old
rm img/weather_out.png.old
rm img/weather.png.old

# save current images as old; mostly useful for debugging
mv img/weather_out.svg img/weather_out.svg.old
mv img/weather_out.png img/weather_out.png.old
mv img/weather.png img/weather.png.old

# downloads the weather and outputs to img/weather_out.svg
OPTIONS="--template img/weather_template.svg"
if [ "${ROTATED:-0}" -ge 1 ]
then
    OPTIONS="$OPTIONS --rotated"
fi

if [ -n "${ZIP+x}" ]
then
    bin/download_weather.py ${OPTIONS} -- "${ZIP}" > img/weather_out.svg
elif [ -n "${LAT+x}" ] && [ -n "${LON+x}" ]
then
    bin/download_weather.py ${OPTIONS} -- "${LAT}" "${LON}" > img/weather_out.svg
elif [ -n "${LOCATION+x}" ] && [ -n "${LOCATION+x}" ]
then
    bin/download_weather.py ${OPTIONS} --key "${KEY}" -- "${LOCATION}" > img/weather_out.svg
else
    >&2 echo "No valid locations defined"
    >&2 echo "Check etc/weather_config"
fi

# convert the svg to a png with white background (no transparency allowed!)
/mnt/us/weather/bin/rsvg-convert --background-color=white -o img/weather_out.png img/weather_out.svg

# change png to greyscale without alpha (color type (-c) 0)
/mnt/us/weather/bin/pngcrush -qf -c 0 img/weather_out.png img/weather.png

# clear the screen twice to prevent ghosting
eips -c
eips -c

# if everything worked, put the weather up; if not, show an error
if [ -e img/weather.png ]; then
	eips -g img/weather.png
else
	eips -g img/error.png
fi
