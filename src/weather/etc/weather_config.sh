##################
# Global Options #
##################

# Uncomment if you want the output roated 180 degrees
# i.e. if you mounted your Kindle upside down
# This variable is checked for being set and not null;
# the value does not matter. For example,
# `ROTATED="0"` would also count as set. `ROTATED=""` would
# count as unset.
#ROTATED="1"

# Uncomment if you want metric units
# (Celsius instead of Farhenheit)
# Only works with AccuWeather and WMO, ignored by Weather.gov
# This variable is checked for being set and not null;
# the value does not matter. For example,
# `METRIC="0"` would also count as set. `METRIC=""` would
# count as unset.
#METRIC="1"

################################################################################
# Uncomment and set ALL the configuration values for ONE of the sections below #
################################################################################

#----------------------------#
# Weather.gov using ZIP code #
#----------------------------#
# Only works in the US

ZIP="10001"

#------------------------------------------#
# Weather.gov using Latitude and Longitude #
#------------------------------------------#
# Only works in the US

#LAT="40.7515634"
#LON="-74.0047868"

#-------------#
# AccuWeather #
#-------------#
# Works worldwide!

# Get an API key from https://www.developer.accuweather.com.
# A free "Limited Trial" plan seems to be sufficient.
# Fill that value in here
#KEY="12345"

# Find the "location key" for your location.
# This can be found by viewing the source of the AccuWeather page
# for your location and finding the canonical link:
# <link rel="canonical" href="https://www.accuweather.com/en/us/new-york/10007/weather-forecast/349727" />
# The final component of the URL, in this case 349727, appears to be the key.
# The "correct" method of finding the location key is to use the Locations API.
# https://developer.accuweather.com/accuweather-locations-api/apis
# You'll only need to do this once, so using the online form from the
# documentation should be sufficient.
#LOCATION="349727"

#----------------------------------#
# World Meterological Organization #
#----------------------------------#
# Works worldwide, without an API key!

# Find the "City ID" for your location.
# Find the closest city to you from the list on the WMO site:
# https://worldweather.wmo.int/en/json/full_city_list.txt
#CITY_ID="278"

