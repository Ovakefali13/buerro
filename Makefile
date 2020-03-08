ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHON ?= $(ROOT_DIR)/venv/bin/python3.7
SERVICE := cal

all: test_services test_usecase
#all: test_single_service

.PHONY: set_buerro_path
set_buerro_path:
	cd $(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") && \
	echo $(ROOT_DIR) > buerro.pth

#test: export DONOTMOCK=1
test: 
	#cd services && $(PYTHON) -m unittest discover -v
	$(PYTHON) `which nosetests` --nologcapture --nocapture -v --with-coverage --cover-min-percentage=75 \
		--cover-package=$(MODULE) $(MODULE)

.PHONY: test_services test_usecase test_single_service
test_services: MODULE=services
test_services: test

test_usecase: MODULE=usecase
test_usecase: test
test_controller: MODULE=controller
test_controller: test

test_single_service: MODULE=services.$(SERVICE)
test_single_service: test

.PHONY: vvs_cal
vvs_cal:
	$(PYTHON) usecase/vvs_cal.py "Hauptbahnhof" "Stadmitte" dep
