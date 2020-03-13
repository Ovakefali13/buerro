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

vapid_app_key:
	vapid/python/venv/bin/vapid --applicationServerKey

vapid_keys: vapid/python/venv/bin/vapid
	$< --gen
        
vapid/python/venv/bin/vapid: 
	cd vapid/python && virtualenv -p 3.7 venv && \
            venv/bin/pip install -r requirements.txt && \
            venv/bin/python setup.py install

.PHONY: backend
backend:
	$(PYTHON) main.py

.PHONY: frontend
frontend:
	cd frontend && npm start
