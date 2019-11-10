#!/usr/bin/env python3
"""Download Weather.

Usage:
    download_weather.py [-r | --rotated] [-t <template> | --template <template>] [--] <zip>
    download_weather.py [-r | --rotated] [-t <template> | --template <template>] [--] <latitude> <longitude>
    download_weather.py [-r | --rotated] [-t <template> | --template <template>] (-m | --metric) (-k <accuweather_key> | --key <accuweather_key>) [--] <location>
    download_weather.py (-h | --help)
    download_weather.py --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -r, --rotated   Rotate the output image 180 degrees.
    -t <template>, --template <template>   Template file. [default: -]
    -k, --key       AccuWeather API key.

Exit Codes:
    0   Success.
    1   General error.
    64  Usage - problem with command arguments.
    69  Unavailable - problem downloading weather data.
"""

from __future__ import annotations

import enum
import json
import logging
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from contextlib import closing
from datetime import date, datetime, timedelta
from itertools import count
from operator import itemgetter
from pathlib import Path, PurePosixPath
from string import Template
from typing import (
    cast,
    Dict,
    List,
    NamedTuple,
    NewType,
    NoReturn,
    Optional,
    Tuple,
    Union,
)
from urllib.error import URLError
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path("../lib").resolve()))

from docopt import docopt


class LatLon(NamedTuple):
    lat: float
    lon: float


ZipCode = NewType("ZipCode", str)
APIKey = NewType("APIKey", str)
LocationKey = NewType("LocationKey", str)
Location = Union[LocationKey, ZipCode, LatLon]


ZIP_URL = "https://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?zipCodeList={zip_}&format=24+hourly&numDays=4&Unit=e"
LATLON_URL = "https://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?lat={lat}&lon={lon}&format=24+hourly&numDays=4&Unit=e"
AU_FORECAST_URL = "https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={api_key}&metric={metric}"

NOMESSAGE = object()

ZIP_RE = re.compile(r"(?P<zip>[0-9]{5})(?:-[0-9]{4})?")

logging.basicConfig(stream=sys.stderr, format="%(levelname)s@%(asctime)s: %(message)s")
logging.captureWarnings(True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Sysexits(enum.Enum):
    """Enumeration of exit codes for `die` following sysexits.h."""

    EX_OK = 0
    EX_GENERAL = 1
    EX_USAGE = 64
    EX_DATAERR = 65
    EX_NOINPUT = 66
    EX_NOUSER = 67
    EX_NOHOST = 68
    EX_UNAVAILABLE = 69
    EX_SOFTWARE = 70
    EX_OSERR = 71
    EX_OSFILE = 72
    EX_CANTCREAT = 73
    EX_IOERR = 74
    EX_TEMPFAIL = 75
    EX_PROTOCOL = 76
    EX_NOPERM = 77
    EX_CONFIG = 78


class WeatherGetter(ABC):
    NUMBERS = ["ONE", "TWO", "THREE", "FOUR"]

    def __init__(self, location: Location, metric: bool = False):
        self.location: Location = location
        self.metric = metric

        self._highs: Optional[Tuple[int, int, int, int]] = None
        self._lows: Optional[Tuple[int, int, int, int]] = None
        self._icons: Optional[Tuple[str, str, str, str]] = None
        self._first_date: Optional[date] = None

    @abstractmethod
    def get_weather(self):
        self._highs: Optional[Tuple[int, int, int, int]] = None
        self._lows: Optional[Tuple[int, int, int, int]] = None
        self._icons: Optional[Tuple[str, str, str, str]] = None
        self._first_date: Optional[date] = None

    @property
    def _weather(self):
        if not self._weather_data:
            self.get_weather()
        return self._weather_data

    @property
    @abstractmethod
    def highs(self) -> Tuple[str, str, str, str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def lows(self) -> Tuple[str, str, str, str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def icons(self) -> Tuple[str, str, str, str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def first_date(self) -> date:
        raise NotImplementedError

    def fill_template(self, template: Template, rotated: bool = False) -> str:
        substitutions: Dict[str, str] = {
            "ROTATION": "180" if rotated else "0",
            "DATE": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "UNIT": "C" if self.metric else "F",
        }
        for i, number, high, low, icon in zip(
            count(), self.NUMBERS, self.highs, self.lows, self.icons
        ):
            substitutions[f"DAY_{number}"] = (
                self.first_date + timedelta(days=i)
            ).strftime("%A")
            substitutions[f"HIGH_{number}"] = high
            substitutions[f"LOW_{number}"] = low
            substitutions[f"ICON_{number}"] = icon

        return template.substitute(substitutions)


class WeatherGovGetter(WeatherGetter):
    def __init__(self, location: Union[ZipCode, LatLon], *args, **kwargs):
        self._weather_data: Optional[ET.ElementTree] = None

        super().__init__(location, *args, **kwargs)

    def get_weather(self):
        if isinstance(self.location, LatLon):
            forecast_request = urllib.request.Request(
                LATLON_URL.format(lat=self.location.lat, lon=self.location.lon)
            )
        else:
            forecast_request = urllib.request.Request(
                ZIP_URL.format(zip_=self.location)
            )

        try:
            with closing(
                urllib.request.urlopen(
                    forecast_request, context=ssl.create_default_context()
                )
            ) as weather_resp:
                resp_code = weather_resp.getcode()
                if resp_code // 100 != 2:
                    die(
                        Sysexits.EX_UNAVAILABLE,
                        "Failed to retrieve weather data: %u %s",
                        resp_code,
                        weather_resp.reason,
                    )
                self._weather_data = ET.parse(weather_resp)
        except URLError as e:
            die(
                Sysexits.EX_UNAVAILABLE,
                "Failed to retrieve weather data: %u %s",
                e.code,
                e.reason,
            )

        super().get_weather()

    @property
    def highs(self):
        if not self._highs:
            self._highs = tuple(
                elem.text
                for elem in self._weather.findall(
                    ".//temperature[@type='maximum']/value"
                )
            )
        return self._highs

    @property
    def lows(self):
        if not self._lows:
            self._lows = tuple(
                elem.text
                for elem in self._weather.findall(
                    ".//temperature[@type='minimum']/value"
                )
            )
        return self._lows

    @property
    def icons(self):
        if not self._icons:
            self._icons = tuple(
                PurePosixPath(urllib.parse.urlsplit(elem.text).path).stem.rstrip(
                    "0123456789"
                )
                for elem in self._weather.findall(".//icon-link")
            )
        return self._icons

    @property
    def first_date(self):
        if not self._first_date:
            self._first_date = date.fromisoformat(
                self._weather.findall(".//start-valid-time")[0].text.split("T")[0]
            )
        return self._first_date


class AccuWeatherGetter(WeatherGetter):
    _icon_mapping: Dict[int, str] = {
        1: "skc",  # sunny
        2: "few",  # mostly sunny
        3: "sct",  # partly sunny
        4: "sct",  # intermittent clouds
        5: "few",  # hazy sunshine
        6: "sct",  # mostly cloudy
        7: "ovc",  # cloudy
        8: "ovc",  # dreary (overcast)
        11: "fg",  # fog
        12: "shra",  # showers
        13: "shra",  # mostly cloudy w/ showers
        14: "hi_shwrs",  # partly sunny w/ showers
        15: "tsra",  # t-storms
        16: "tsra",  # mostly cloudy w/ t-storms
        17: "tsra",  # partly sunny w/ t-storms
        18: "ra",  # rain
        19: "sn",  # flurries
        20: "sn",  # mostly cloudy w/ flurries
        21: "sn",  # partly sunny w/ flurries
        22: "blizzard",  # snow
        23: "sn",  # mostly cloudy w/ snow
        24: "ip",  # ice
        25: "fzra",  # sleet
        26: "fzra",  # freezing rain
        29: "mix",  # rain and snow
        30: "hot",  # hot
        31: "cold",  # cold
        32: "wind",  # windy
        33: "skc",  # clear
        34: "few",  # mostly clear
        35: "sct",  # partly cloudy
        36: "sct",  # intermittent clouds
        37: "few",  # hazy moonlight
        38: "sct",  # mostly cloudy
        39: "hi_shwrs",  # partly cloudy w/ showers
        40: "shra",  # mostly cloudy w/ showers
        41: "tsra",  # partly cloudy w/ t-storms
        42: "tsra",  # mostly cloudy w/ t-storms
        43: "sn",  # mostly cloudy w/ flurries
        44: "sn",  # mostly cloudy w/ snow
    }

    def __init__(self, api_key: str, location: LocationKey, *args, **kwargs):
        self.api_key = api_key

        self._weather_data: Optional[dict] = None

        super().__init__(location, *args, **kwargs)

    def get_weather(self):
        forecast_request = urllib.request.Request(
            AU_FORECAST_URL.format(
                location_key=self.location,
                api_key=self.api_key,
                metric=str(self.metric).lower(),
            )
        )
        try:
            with closing(
                urllib.request.urlopen(
                    forecast_request, context=ssl.create_default_context()
                )
            ) as weather_resp:
                resp_code = weather_resp.getcode()
                if resp_code // 100 != 2:
                    die(
                        Sysexits.EX_UNAVAILABLE,
                        "Failed to retrieve weather data: %u %s",
                        resp_code,
                        weather_resp.reason,
                    )
                weather_data = json.load(weather_resp)
                self._weather_data = weather_data
        except URLError as e:
            die(
                Sysexits.EX_UNAVAILABLE,
                "Failed to retrieve weather data: %u %s",
                e.code,
                e.reason,
            )

        super().get_weather()

    @property
    def highs(self):
        if not self._highs:
            sorted_forecasts = sorted(
                self._weather["DailyForecasts"], key=itemgetter("Date")
            )
            self._highs = tuple(
                str(int(forecast["Temperature"]["Maximum"]["Value"]))
                for forecast in sorted_forecasts
            )
        return self._highs

    @property
    def lows(self):
        if not self._lows:
            sorted_forecasts = sorted(
                self._weather["DailyForecasts"], key=itemgetter("Date")
            )
            self._lows = tuple(
                str(int(forecast["Temperature"]["Minimum"]["Value"]))
                for forecast in sorted_forecasts
            )
        return self._lows

    @property
    def icons(self):
        if not self._icons:
            sorted_forecasts = sorted(
                self._weather["DailyForecasts"], key=itemgetter("Date")
            )
            self._icons = tuple(
                self._icon_mapping[forecast["Day"]["Icon"]]
                for forecast in sorted_forecasts
            )
        return self._icons

    @property
    def first_date(self):
        if not self._first_date:
            self._first_date = datetime.fromisoformat(
                self._weather["Headline"]["EffectiveDate"]
            ).date()
        return self._first_date


def die(
    code: Sysexits = Sysexits.EX_GENERAL,
    msg: Union[object, str] = NOMESSAGE,
    *args,
    **kwargs,
) -> NoReturn:
    """Log an error message and exit.

    :param code: The code to exit with
    :param msg: The message format string to log
    :param *args: Additional positional arguments to the logging call
    :param **kwargs: Additional keyword arguments to the logging call

    :returns: Never returns
    """

    if msg is not NOMESSAGE:
        logger.error(msg, *args, **kwargs)

    sys.exit(code)


def main(argv: List[str]) -> Optional[int]:
    arguments = docopt(__doc__, argv=argv[1:], version="Download Weather 1.0.0")

    weather_getter: WeatherGetter

    if (
        arguments["<location>"]
        and arguments["--key"]
        and arguments["<accuweather_key>"]
    ):
        location = cast(LocationKey, arguments["<location>"])
        key = cast(APIKey, arguments["<accuweather_key>"])
        metric = cast(bool, arguments["--metric"])
        logger.info('Weather Underground: "%s"', location)
        weather_getter = AccuWeatherGetter(key, location, metric=metric)
    elif arguments["<zip>"]:
        zip_ = cast(str, arguments["<zip>"])
        zip_ = zip_.strip()
        match = ZIP_RE.fullmatch(zip_)
        if not match:
            die(Sysexits.EX_USAGE, 'Invalid ZIP Code: "%s"', zip_)
        zip_ = cast(ZipCode, match.group("zip"))

        logger.info('Weather.gov: "%s"', zip_)
        weather_getter = WeatherGovGetter(zip_)
    elif arguments["<latitude>"] and arguments["<longitude>"]:
        lat_str = cast(str, arguments["<latitude>"])
        lon_str = cast(str, arguments["<longitude>"])
        try:
            lat = float(lat_str)
        except ValueError:
            die(Sysexits.EX_USAGE, 'Invalid latitude: "%s"', lat)
        try:
            lon = float(lon_str)
        except ValueError:
            die(Sysexits.EX_USAGE, 'Invalid longitude: "%s"', lon)

        logger.info('Weather.gov: "%f/%f"', lat, lon)
        latlon = LatLon(lat, lon)
        weather_getter = WeatherGovGetter(latlon)
    else:
        # this shouldn't happen because of docopt
        die(Sysexits.EX_USAGE, "No location on command line")

    template_path = cast(str, arguments["--template"])
    if template_path == "-":
        if sys.stdin.isatty():
            logger.warning("Reading template from a terminal")
        template_string = sys.stdin.read()
    else:
        with open(template_path) as f:
            template_string = f.read()

    template = Template(template_string)

    output = weather_getter.fill_template(template, cast(bool, arguments["--rotated"]))
    print(output, flush=True)

    return None


if __name__ == "__main__":
    sys.exit(main(sys.argv))
