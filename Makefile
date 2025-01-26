.PHONY: all clean distclean

DISTDIR := dist

UPDATE_DEPS = $(shell find src/extensions src/weather -path '__pycache__' -prune -o ! -name '*.pyc' ! -name '.DS_Store' ! -name '*.swp')

OLD_DEVICES := --device touch --device paperwhite
#NEW_DEVICES := --device paperwhite2 --device basic --device voyage --device paperwhite3 --device oasis --device basic2 --device oasis2 --device paperwhite4 --device basic3 --device oasis3 --device paperwhite5 --device basic4 --device scribe
NEW_DEVICES := --device paperwhite2 --device basic --device voyage --device paperwhite3 --device oasis --device basic2 --device oasis2 --device paperwhite4 --device basic3 --device oasis3

all: \
	dist/Update_weather_touch_pw_install.bin dist/Update_weather_touch_pw_uninstall.bin \
	dist/Update_weather_pw2_and_up_install.bin dist/Update_weather_pw2_and_up_uninstall.bin

dist/Update_weather_touch_pw_install.bin: src/install.sh src/libotautils src/weather.tar.xz src/xzdec | DISTDIR
	cd src && kindletool create ota2 $(OLD_DEVICES) $(notdir $^) ../$@

dist/Update_weather_touch_pw_uninstall.bin: src/uninstall.sh src/libotautils | DISTDIR
	cd src && kindletool create ota2 $(OLD_DEVICES) $(notdir $^) ../$@

dist/Update_weather_pw2_and_up_install.bin: src/install.sh src/libotautils src/weather.tar.xz src/xzdec | DISTDIR
	cd src && kindletool create ota2 $(NEW_DEVICES) $(notdir $^) ../$@

dist/Update_weather_pw2_and_up_uninstall.bin: src/uninstall.sh src/libotautils | DISTDIR
	cd src && kindletool create ota2 $(NEW_DEVICES) $(notdir $^) ../$@

src/weather.tar.xz: $(UPDATE_DEPS)
	tar --create --xz --directory=src --exclude '*.pyc' --exclude '__pycache__' --verbose --file=$@ weather extensions

DISTDIR:
	mkdir -p dist

clean:
	git clean -fx

distclean:
	git clean -fdx

