ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHON ?= $(ROOT_DIR)/venv/bin/python3.7

ifdef MODULE
    ARGS := --module $(MODULE)
endif

all: mock no_mock

.PHONY: mock no_mock
mock:
	$(PYTHON) test_loader.py $(ARGS)

no_mock: 
	DONOTMOCK=1 $(PYTHON) test_loader.py $(ARGS)

.PHONY: set_buerro_path
set_buerro_path:
	cd $(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") && \
            echo $(ROOT_DIR) > buerro.pth
