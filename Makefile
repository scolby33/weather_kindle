.PHONY: clean directories

EXTENSION_DIRS = $(shell find src/extensions -type d)
EXTENSION_FILES = $(shell find src/extensions -type f -name '*')
WEATHER_DIRS = $(shell find src/weather -type d)
WEATHER_FILES = $(shell find src/weather -type f -name '*')

all: Update_weather_k4_install.bin

Update_weather_k4_install.bin: src/install.sh src/libotautils src/weather.tar.xz src/xzdec
	cd src && kindletool create ota2 -d kindle4 install.sh libotautils xzdec weather.tar.xz ../Update_weather_k4_install.bin

src/weather.tar.xz: $(EXTENSION_DIRS) $(EXTENSION_FILES) $(WEATHER_DIRS) $(WEATHER_FILES)
	cd src; tar -cvJf weather.tar.xz weather extensions

clean:
	rm src/weather.tar.xz
	rm Update_weather_k4_install.bin

