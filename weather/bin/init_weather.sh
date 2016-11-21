#!/bin/sh

/etc/init.d/framework stop  # kill the Kindle menus
/etc/init.d/powerd stop  # keep the screen from turning off

/mnt/us/weather/bin/update_weather.sh  # get the weather
