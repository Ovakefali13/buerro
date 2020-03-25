ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHON ?= $(ROOT_DIR)/venv/bin/python3.7
#MODULE=controller

ifdef MODULE
    ARGS := --module $(MODULE)
endif

default: mock 
integration: mock no_mock

.PHONY: mock no_mock
mock:
	$(PYTHON) test_loader.py $(ARGS)
no_mock: 
	DONOTMOCK=1 $(PYTHON) test_loader.py $(ARGS)

.PHONY: vapid_app_key
vapid_app_key: sec/vapid_public_key.pem
	vapid/python/venv/bin/vapid --applicationServerKey

sec/vapid_public_key.pem: vapid/python/venv/bin/vapid sec
	$< --gen && for file in *_key.pem; do mv "$$file" "sec/vapid_$$file"; done

sec:
	mkdir $@
        
vapid/python/venv/bin/vapid: vapid/python
	cd vapid/python && virtualenv -p 3.7 venv && \
            venv/bin/pip install -r requirements.txt && \
            venv/bin/python setup.py install

vapid/python:
	git submodule update --init --remote --recursive

# https://stackoverflow.com/a/43666288
.PHONY: cert
cert:
	@echo "FOR COMMON NAME ENTER: localhost"
	cd frontend/ssl && bash create_root_cert_and_key.sh
	cd frontend/ssl && bash create_certificate_for_domain.sh localhost 

.PHONY: backend
backend:
	PRODUCTION=1 $(PYTHON) main.py

.PHONY: frontend
frontend:
	PRODUCTION=1 cd frontend && npm start
