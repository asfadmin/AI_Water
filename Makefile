install:
	ln -s `pwd`/prepare_data.py ~/.local/bin/
	chmod u+x ~/.local/bin/prepare_data.py

uninstall:
	rm ~/.local/bin/prepare_data.py
