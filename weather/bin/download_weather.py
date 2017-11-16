#!/usr/bin/env python2
"""Download Weather.

Usage:
    download_weather.py [-r | --rotated] [-t | --template <template>] [--] <zip>
    download_weather.py [-r | --rotated] [-t | --template <template>] [--] <latitude> <longitude>
    download_weather.py [-r | --rotated] [-t | --template <template>] (-k | --key <wunderground_key>) [--] <location>
    download_weather.py (-h | --help)
    download_weather.py --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -r, --rotated   Rotate the output image 180 degrees.
    -t <template>, --template <template>   Template file. [default: stdin]
    -k, --key       Weather Underground API key

"""

from __future__ import print_function, unicode_literals

from contextlib import closing
from datetime import datetime, timedelta
import io
from itertools import count, izip
import json
import os
import urllib2
import string
import sys
import xml.etree.ElementTree as ET

sys.path.insert(
    0,
    os.path.realpath(os.path.join(
        os.path.dirname(os.path.realpath(sys.argv[0])),
        '../lib'
    ))
)

from docopt import docopt

ZIP_URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?zipCodeList={zip}&format=24+hourly&numDays=4&Unit=e'
LATLON_URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?lat={lat}&lon={lon}&format=24+hourly&numDays=4&Unit=e'
WU_URL = 'https://api.wunderground.com/api/{key}/conditions/forecast/q/{location}.json'

class WeatherGetter(object):
    def __init__(self, location):
        self.location = location
        
        self._weather_data = None
        
        self._highs = None
        self._lows = None
        self._icons = None
        self._first_date = None
        
    def _update_weather(self):
        self._highs, self._lows, self._icons = [None] * 3
        
    @property
    def _weather(self):
        if not self._weather_data:
            self._update_weather()
        return self._weather_data
        
    def fill_template(self, template_string, rotated=False):
        template = string.Template(template_string)
        substitutions = {
            'ROTATION': 180 if rotated else 0,
            'DATE': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        numbers = ['ONE', 'TWO', 'THREE', 'FOUR']
        for i, number, high, low, icon in izip(
            count(),
            numbers,
            self.highs,
            self.lows,
            self.icons
        ):
            substitutions['DAY_{}'.format(number)] = (self.first_date + timedelta(days=i)).strftime('%A')
            substitutions['HIGH_{}'.format(number)] = high
            substitutions['LOW_{}'.format(number)] = low
            substitutions['ICON_{}'.format(number)] = icon

        return template.substitute(substitutions)
        

class WeatherGovGetter(WeatherGetter):
    def _update_weather(self):
        if isinstance(self.location, tuple):
            lat, lon = self.location
            with closing(urllib2.urlopen(LATLON_URL.format(lat=lat, lon=lon))) as weather_xml:
                self._weather_data = ET.parse(weather_xml)
        else:
            with closing(urllib2.urlopen(ZIP_URL.format(zip=self.location))) as weather_xml:
                self._weather_data = ET.parse(weather_xml)
        
        super(WeatherGovGetter, self)._update_weather()
        
    @property
    def highs(self):
        if not self._highs:
            self._highs = [inner_text for temp_elem in self._weather.iter(tag='temperature')
                           for value_elem in temp_elem.iter(tag='value')
                           for inner_text in value_elem.itertext()
                           if temp_elem.get('type') == 'maximum']
        return self._highs
        
    @property
    def lows(self):
        if not self._lows:
            self._lows = [inner_text for temp_elem in self._weather.iter(tag='temperature')
                           for value_elem in temp_elem.iter(tag='value')
                           for inner_text in value_elem.itertext()
                           if temp_elem.get('type') == 'minimum']
        return self._lows
        
    @property
    def icons(self):
        if not self._icons:
            self._icons = [icon_elem.text.split('/')[-1].split('.')[0].rstrip('0123456789')
                           for icon_elem in self._weather.iter(tag='icon-link')]
        return self._icons
        
    @property
    def first_date(self):
        if not self._first_date:
            self._first_date = datetime.strptime(
                next(self._weather.iter('start-valid-time')).text.split('T')[0],
                '%Y-%m-%d'
            )
        return self._first_date
              
    
class WundergroundGetter(WeatherGetter):
    _icon_mapping = {
        'chanceflurries': 'sn',
        'chancerain': 'hi_shwrs',
        'chancesleet': 'mix',
        'chancesleet': 'mix',
        'chancesnow': 'sn',
        'chancesnow': 'sn',
        'chancetstorms': 'hi_tsra',
        'chancetstorms': 'hi_tsra',
        'clear': 'skc',
        'cloudy': 'sct',
        'flurries': 'sn',
        'fog': 'fg',
        'hazy': 'mist',
        'mostlycloudy': 'bkn',
        'mostlysunny': 'few',
        'partlycloudy': 'sct',
        'partlysunny': 'sct',
        'sleet': 'mix',
        'rain': 'ra',
        'sleet': 'mix',
        'snow': 'sn',
        'sunny': 'skc',
        'tstorms': 'tsra',
        'tstorms': 'tsra',
        'cloudy': 'ovc',
        'partlycloudy': 'sct'
    }
    def __init__(self, key, location):
        self._key = key
        super(WundergroundGetter, self).__init__(location)
        
    def _update_weather(self):
        with closing(urllib2.urlopen(WU_URL.format(key=self._key, location=self.location))) as weather_json:
            self._weather_data = json.load(weather_json)
            if self._weather['response'].get('error', None):
                raise ValueError('Bad key `{}` supplied!'.format(self._key))
        super(WundergroundGetter, self)._update_weather()
        
    @property
    def highs(self):
        if not self._highs:
            self._highs = [day['high']['fahrenheit'] for
                           day in self._weather['forecast']['simpleforecast']['forecastday']]
        return self._highs
        
    @property
    def lows(self):
        if not self._lows:
            self._lows = [day['low']['fahrenheit'] for
                           day in self._weather['forecast']['simpleforecast']['forecastday']]
        return self._lows
        
    @property    
    def icons(self):
        if not self._icons:
            icons = [day['icon'] for
                     day in self._weather['forecast']['simpleforecast']['forecastday']]
            self._icons = [self._icon_mapping[icon] for icon in icons]
        return self._icons
        
    @property    
    def first_date(self):
        if not self._first_date:
            date = self._weather['forecast']['simpleforecast']['forecastday'][0]['date']
            self._first_date = datetime(year=date['year'], month=date['month'], day=date['day'])
        return self._first_date


def main(argv):
    arguments = docopt(__doc__, version='Download Weather 0.1.0')
    if arguments['<location>']:
        # using Weather Underground
        weather_getter = WundergroundGetter(arguments['<wunderground_key>'], arguments['<location>'])
    else:
        # using weather.gov
        if arguments['<zip>']:
            weather_getter = WeatherGovGetter(arguments['<zip>'])
        else:
            weather_getter = WeatherGovGetter((arguments['<latitude>'], arguments['<longitude>']))
            
    if arguments['--template'][0] == 'stdin':
        template_string = sys.stdin.read()
    else:
        with io.open(arguments['--template'][0], 'r', encoding='utf-8') as f:
            template_string = f.read()
            
    output = weather_getter.fill_template(template_string, arguments['--rotated'])
    sys.stdout.write(output.encode('utf-8'))
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
