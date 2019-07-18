install:
	ln -s `pwd`/tile_geotiff.py ~/.local/bin/
	chmod u+x ~/.local/bin/tile_geotiff.py

uninstall:
	rm ~/.local/bin/tile_geotiff.py
