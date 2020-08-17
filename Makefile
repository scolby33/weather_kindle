.PHONY: all clean distclean

DISTDIR := dist

UPDATE_DEPS = $(shell find src/extensions src/weather -path '__pycache__' -prune -o ! -name '*.pyc' ! -name '.DS_Store' ! -name '*.swp')

all: dist/Update_weather_k4_kt_install.bin dist/Update_weather_k4_kt_uninstall.bin

dist/Update_weather_k4_kt_install.bin: src/install.sh src/libotautils src/weather.tar.xz src/xzdec | DISTDIR
	cd src && kindletool create ota2 --device kindle4 --device touch $(notdir $^) ../$@

dist/Update_weather_k4_kt_uninstall.bin: src/uninstall.sh src/libotautils | DISTDIR
	cd src && kindletool create ota2 --device kindle4 --device touch $(notdir $^) ../$@

src/weather.tar.xz: $(UPDATE_DEPS)
	tar --create --xz --directory=src --exclude '*.pyc' --exclude '__pycache__' --verbose --file=$@ weather extensions

DISTDIR:
	mkdir -p dist

clean:
	git clean -fx

distclean:
	git clean -fdx

