PREFIX ?= /usr

BIN_DIR = $(PREFIX)/bin
UNIT_DIR = $(PREFIX)/lib/systemd/user
MAN_DIR = $(PREFIX)/share/man
LICENSE_DIR = $(PREFIX)/share/licenses/codot
SHARE_DIR = $(PREFIX)/share/codot

INSTALL_DATA = install -m 644 -D
INSTALL_BIN = install -m 755 -D

build:
	make -C "docs" man
	sed "s|@bindir@|$(BIN_DIR)|" "docs/unit/codot.service.in" > "docs/unit/codot.service"
	python3 setup.py build
	python3 setup.py egg_info

install:
	python3 setup.py install \
		--prefix "$(PREFIX)" \
		--single-version-externally-managed \
		--record "installed_files.txt"
	$(INSTALL_BIN) "scripts/codot" -t "$(BIN_DIR)"
	$(INSTALL_BIN) "scripts/codotd" -t "$(BIN_DIR)"
	$(INSTALL_DATA) "docs/_build/man/codot.1" -t "$(MAN_DIR)/man1"
	$(INSTALL_DATA) "docs/unit/codot.service" -t "$(UNIT_DIR)"
	$(INSTALL_DATA) "LICENSE" -t "$(LICENSE_DIR)"
	$(INSTALL_DATA) "docs/config/settings.conf" -t "$(SHARE_DIR)"
	gzip -9f "$(MAN_DIR)/man1/codot.1"

uninstall:
	cat "installed_files.txt" | xargs rm -rf
	rm -f "installed_files.txt"
	rm -f "$(BIN_DIR)/codot"
	rm -f "$(BIN_DIR)/codotd"
	rm -f "$(MAN_DIR)/man1/codot.1.gz"
	rm -f "$(UNIT_DIR)/codot.service"
	rm -rf "$(LICENSE_DIR)"
	rm -rf "$(SHARE_DIR)"

clean:
	rm -rf "build"
	rm -rf "docs/_build"
	rm -f "docs/unit/codot@.service"
	find "codot" -depth -name "__pycache__" -type d | xargs rm -rf

develop:
	python3 setup.py develop \
		--prefix "$(PREFIX)" \
		--user

help:
	@echo "make:            Build the program."
	@echo "make install:    Install the program normally."
	@echo "make uninstall:  Uninstall the program."
	@echo "make clean:      Remove generated files."
	@echo "make develop:	Install the program in development mode."
	@echo "make help:       Show this help message."

.PHONY: build install uninstall clean develop help
