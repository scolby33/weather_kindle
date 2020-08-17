# Weather Kindle

Use your Kindle to display a weather forecast, no server required!

## Installation

### Prerequisites
You must have a jailbroken Kindle 4 with Python 3 installed.
Visit [the MobileRead forums](http://www.mobileread.com/forums/showthread.php?t=88004) for information on accomplishing this.

This software has only been tested on a Kindle 4, but will likely work with some modification on other versions of Kindles. Due to architectural differences between Kindles, the `rsvg-convert` and `pngcrush` binaries and the shared libraries in `lib` might need to be replaced.

### Initial Setup

1. Change the ZIP code at the top of `weather/bin/update_weather.sh` to match your location.
2. Copy the `weather` folder and its contents to the root of your Kindle's USB storage (`/mnt/us/`, if using SCP).
3. SSH into your Kindle and run `mntroot rw` and append the following line to `/etc/crontab/root`.

    ```
    0 * * * * /mnt/us/weather/bin/update_weather.sh  # update the weather display at the top of every hour
    ```
4. Make sure your Kindle is connected to an active Wi-Fi network.
5. Run `/mnt/us/weather/bin/init_weather.sh`.

### Temporarily Disabling the Weather Display

1. SSH into your Kindle and run `mntroot rw`.
2. Comment out or remove the line you added to `/etc/crontab/root`.
3. Restart your Kindle, either by running `restart` via SSH or holding the power button.


### Full Uninstallation

1. SSH into your Kindle and run `mntroot rw`.
2. Comment out or remove the line you added to `/etc/crontab/root`.
3. Run `mntroot ro`.
4. Run `rm -r /mnt/us/weather`.
5. Follow the directions to uninstall USBNetwork, Python, and the Jailbreak, which were provided with each of the installation packages.

# History and Current Status

This project is based on and inspired by Matthew Petroff's [Kindle Weather Display](https://mpetroff.net/2012/09/kindle-weather-display/) (also [on Github](https://github.com/mpetroff/kindle-weather-display)).
I was disappointed, however, by the need for an external server to download the weather information and process the images.
Putting together some ARM binaries from the Debian APT repository, a few shell scripts, and a few weeks of sporadic hacking, I created the first version of this program, which created the weather summary entirely on the Kindle.

A few years later, I dug this out and re-wrote significant portions of the code and have put it together to post on GitHub and on the Mobile Read forums.

I am currently in the process of packaging this up as a Kindle "update" for easier installation and adding [KUAL](http://www.mobileread.com/forums/showthread.php?t=203326) compatibility. This should also help with the creation of versions for other types of Kindles.

# License

The weather image template and icons, which were originally created by Matthew Petroff, are used under the CC0 Public Domain Dedication. My modifications to the weather image template are also dedicated to the public under the CC0 Public Domain Dedication. The original source is found at https://github.com/mpetroff/kindle-weather-display.

RSVG is used under the terms of the GNU General Public License. There have been no modifications to RSVG as obtained from the original creators.

Pngcrush is used under the terms of the Pngcrush license, which allows for use and distribution of the program with no fee. There have been no modifications to Pngcrush as obtained from the original creators.

The remainder of weather_kindle is Copyright (c) 2019 Scott Colby and is available under the MIT license.

See the [LICENSE.md](LICENSE.md) file for the full text of the license.

