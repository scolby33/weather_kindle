#!/usr/bin/env python2
"""Download Weather.

Usage:
    download_weather.py [-r | --rotated] [-t | --template <template>] [--] <zip>
    download_weather.py [-r | --rotated] [-t | --template <template>] [--] <latitude> <longitude>
    download_weather.py (-h | --help)
    download_weather.py --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -r, --rotated   Rotate the output image 180 degrees.
    -t <template>, --template <template>   Template file. [default: stdin]

"""

from __future__ import print_function, unicode_literals

import codecs
from datetime import datetime, timedelta
from itertools import count, izip
import urllib2
import string
import sys
import xml.etree.ElementTree as ET

from docopt import docopt

ZIP_URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?zipCodeList={zip}&format=24+hourly&numDays=4&Unit=e'
LATLON_URL = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?lat={lat}&lon={lon}&format=24+hourly&numDays=4&Unit=e'


def get_weather(location):
    if isinstance(location, tuple):
        lat, lon = location
        weather_xml = urllib2.urlopen(
            LATLON_URL.format(lat=lat, lon=lon)
        )
    else:
        weather_xml = urllib2.urlopen(
            ZIP_URL.format(zip=location)
        )

    return ET.parse(weather_xml)


def get_highs_lows(weather_tree):
    highs = (inner_text for temp_elem in weather_tree.iter(tag='temperature')
             for value_elem in temp_elem.iter(tag='value')
             for inner_text in value_elem.itertext()
             if temp_elem.get('type') == 'maximum')
    lows = (inner_text for temp_elem in weather_tree.iter(tag='temperature')
            for value_elem in temp_elem.iter(tag='value')
            for inner_text in value_elem.itertext()
            if temp_elem.get('type') == 'minimum')
    return highs, lows


def get_icons(weather_tree):
    return (icon_elem.text.split('/')[-1].split('.')[0].rstrip('0123456789')
            for icon_elem in weather_tree.iter(tag='icon-link'))


def get_first_date(weather_tree):
    return datetime.strptime(
        next(weather_tree.iter('start-valid-time')).text.split('T')[0],
        '%Y-%m-%d'
    )


def fill_template(template_string, highs, lows, icons, start_date, rotate=False):
    template = string.Template(template_string)
    substitutions = {
        'ROTATION': 180 if rotate else 0,
        'DATE': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    numbers = ['ONE', 'TWO', 'THREE', 'FOUR']
    for i, number, high, low, icon in izip(count(), numbers, highs, lows, icons):
        substitutions['DAY_{}'.format(number)] = (start_date + timedelta(days=i)).strftime('%A')
        substitutions['HIGH_{}'.format(number)] = high
        substitutions['LOW_{}'.format(number)] = low
        substitutions['ICON_{}'.format(number)] = icon

    return template.substitute(substitutions)


def main(argv):
    arguments = docopt(__doc__, version='Download Weather 0.1.0')
    if arguments['<zip>']:
        weather_tree = get_weather(arguments['<zip>'])
    else:
        weather_tree = get_weather((arguments['<latitude>'], arguments['<longitude>']))

    # parse temps
    highs, lows = get_highs_lows(weather_tree)

    # parse icons
    icons = get_icons(weather_tree)

    # parse dates
    start_valid_date = get_first_date(weather_tree)

    if arguments['--template'][0] == 'stdin':
        template_string = sys.stdin.read()
    else:
        with codecs.open(arguments['--template'][0], 'r', encoding='utf-8') as f:
            template_string = f.read()

    output = fill_template(
        template_string,
        highs,
        lows,
        icons,
        start_valid_date,
        arguments['--rotated']
    )

    sys.stdout.write(output.encode('utf-8'))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
