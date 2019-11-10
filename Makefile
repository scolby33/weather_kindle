.PHONY: clean distclean

DISTDIR := dist

UPDATE_DEPS = $(shell find src/extensions src/weather -path '__pycache__' -prune -o ! -name '.DS_Store' ! -name '*.swp')

dist/Update_weather_k4_install.bin: src/install.sh src/libotautils src/weather.tar.xz src/xzdec | DISTDIR
	cd src && kindletool create ota2 --device kindle4 $(notdir $^) ../$@

src/weather.tar.xz: $(UPDATE_DEPS)
	tar --create --xz --directory=src --file=$@ weather extensions

DISTDIR:
	mkdir -p dist

clean:
	git clean -fx

distclean:
	git clean -fdx

