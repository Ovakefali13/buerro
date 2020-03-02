ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHON:=$(ROOT_DIR)/venv/bin/python3.7

all: test_adapter test_usecase

.PHONY: set_buerro_path
set_buerro_path:
	cd $(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") && \
	echo $(ROOT_DIR) > buerro.pth

<<<<<<< Updated upstream
.PHONY: test
test:
	cd adapter && $(PYTHON) -m unittest discover
=======
#test: export DONOTMOCK=1
test: 
	#cd adapter && $(PYTHON) -m unittest discover -v
	$(PYTHON) `which nosetests` --nocapture -v --with-coverage --cover-min-percentage=75 \
		--cover-package=$(MODULE)

.PHONY: test_adapter test_usecase
test_adapter: MODULE=adapter
test_adapter: test
test_usecase: MODULE=usecase
test_usecase: test




.PHONY: vvs_cal
vvs_cal:
	$(PYTHON) usecase/vvs_cal.py "Hauptbahnhof" "Stadmitte" dep
>>>>>>> Stashed changes
