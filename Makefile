VENV=.venv
PYPI_USER=$(shell echo ${TWINE_USERNAME} | base64 -d)
PYPI_PASS=$(shell echo ${TWINE_PASSWORD} | base64 -d)

.PHONY: init-venv
init-venv:
	@echo "Start init-venv..."
	@test -d ${VENV} && echo "Virtual environment is exists." \
		|| python3 -m venv ${VENV}
	@. ${VENV}/bin/activate \
		&& echo "Installing python libraries..." \
		&& pip install -q --upgrade pip \
		&& pip install -q -r requirements.txt
	@echo "Finish init-venv"

.PHONY: clean
clean:
	@echo "Start clean..."
	rm -rf build dist VERSION.txt
	find . -name '__pycache__' -type d |xargs rm -rf
	find . -name '*.egg-info' -type d |xargs rm -rf
	find . -name '*.egg-info' -type f -delete
	find . -name '*~' -type f -delete
	find ./pychromedriver -name 'chromedriver_*' -type f -delete
	@echo "Finish clean"

.PHONY: build
build: init-venv
	@echo "Start build..."
	@. ${VENV}/bin/activate \
		&& python ./update.py \
		&& python ./setup.py sdist bdist_wheel \
		|| :
	@echo "Finish build"

.PHONY: upload-test
upload-test: clean build
	@echo "Start upload-test..."
	@test -f VERSION.txt \
		&& . ${VENV}/bin/activate \
		&& python -m twine upload \
			-u ${PYPI_USER} \
			-p ${PYPI_PASS} \
			--repository-url 'https://test.pypi.org/legacy/' \
			dist/* \
		|| :
	@echo "Finish upload-test"

.PHONY: upload-pypi
upload-pypi: clean build
	@echo "Start upload-pypi..."
	@test -f VERSION.txt \
		&& . ${VENV}/bin/activate \
		&& python -m twine upload \
			-u ${PYPI_USER} \
			-p ${PYPI_PASS} \
			dist/* \
		|| :
	@echo "Finish upload-pypi"
