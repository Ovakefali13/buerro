ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHON:=$(ROOT_DIR)/venv/bin/python3.7

all: test

.PHONY: set_buerro_path
set_buerro_path:
	cd $(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") && \
	echo $(ROOT_DIR) > buerro.pth

.PHONY: test
test:
	cd adapter && $(PYTHON) -m unittest discover -v

.PHONY: vvs_cal
vvs_cal:
	$(PYTHON) usecase/vvs_cal.py "Hauptbahnhof" "Stadmitte" dep
