# Weather Kindle

Use your Kindle to display a weather forecast!

## Installation

### Prerequisites
You must have a jailbroken Kindle with Python 3 installed. Visit [the MobileRead forums](https://www.mobileread.com/forums/showthread.php?t=320564) for information on accomplishing this.

This software has only been tested on a Kindle 4, but will likely work with some modification on other models of Kindle. Due to architectural differences between Kindle models, the `rsvg-convert` and `pngcrush` binaries and the shared libraries in `lib` might need to be replaced. If you have a different Kindle model that you'd like to use this program with, please open an issue and I will do my best to adapt it for your device!

### Installing a Release `.bin`

1. Download the appropriate `Update_weather_{device abbreviation}_install.bin` installer from the [releases page](https://github.com/scolby33/weather_kindle/releases) of this repo.
2. Transfer the installer to your Kindle via USB. Place it in the `mrpackages` directory at the root of your Kindle.
3. Run the installer using the MobileRead Package Installer (MRPI) using the "Install MR Packages" option in KUAL.
4. Continue to [configuration](#configuration), below.

### Configuration

The installer will have created a configuration file at `weather/etc/weather_config.sh`. Connect to your Kindle via USB and open this file in a text editor. Follow the instructions within to configure your location and what weather service you want to use to obtain the local weather data. The current best choice is the World Meteorological Organization, which seems to have the most stable API.

### Begin Displaying the Weather

Disconnect your Kindle from your computer and open KUAL. The installer will have created a "Weather" entry in the menu. There are two steps to perform:

1. Choose the "Install in Crontab" option to set up hourly updates of the weather.
2. Choose the "Start Weather Display" option to bring the weather display full screen and put your Kindle in weather mode.

### Stop Displaying the Weather

To exit weather mode, you must reboot your Kindle. Perform whatever steps are necessary for your device; on my Kindle 4, this requires pressing and holding the power button for several seconds. Once your Kindle has rebooted, open KUAL and choose "Remove from Crontab" from the Weather menu. This will prevent your Kindle from interrupting you every hour trying to display the weather. After this, you can use your Kindle as normal.

### Uninstallation

1. Download the latest version of the appropriate `Update_weather_{device abbreviation}_uninstall.bin` uninstaller from the [releases page](https://github.com/scolby33/weather_kindle/releases) of this repo.
2. Transfer the uninstaller to your Kindle via USB. Place it in the `mrpackages` directory at the root of your Kindle.
3. Run the uninstaller using the MobileRead Package Installer (MRPI) using the "Install MR Packages" option in KUAL. Even though this option is called "install," if you loaded the uninstaller to your Kindle, the uninstallation process will take place.

## History and Current Status

This project is based on and inspired by Matthew Petroff's [Kindle Weather Display](https://mpetroff.net/2012/09/kindle-weather-display/) (also [on Github](https://github.com/mpetroff/kindle-weather-display)).
I was disappointed, however, by the need for an external server to download the weather information and process the images.
Putting together some ARM binaries from the Debian APT repository, a few shell scripts, and a few weeks of sporadic hacking, I created the first version of this program, which created the weather summary entirely on the Kindle.

A few years later, I dug this out and re-wrote significant portions of the code and have put it together to post on GitHub and on the Mobile Read forums.

Most recently, I have created `.bin` installers and uninstallers and released them as built artifacts on GitHub.

## License

The weather image template and icons, which were originally created by Matthew Petroff, are used under the CC0 Public Domain Dedication. My modifications to the weather image template are also dedicated to the public under the CC0 Public Domain Dedication. The original source is found at https://github.com/mpetroff/kindle-weather-display.

RSVG is used under the terms of the GNU General Public License. There have been no modifications to RSVG as obtained from the original creators.

Pngcrush is used under the terms of the Pngcrush license, which allows for use and distribution of the program with no fee. There have been no modifications to Pngcrush as obtained from the original creators.

Docopt is used under the terms of the MIT license. There have been no modifications to docopt as obtained from the original creators.

The remainder of weather_kindle is Copyright (c) 2020 Scott Colby and is available under the MIT license.

See the [LICENSE.md](LICENSE.md) file for the full text of the license.

