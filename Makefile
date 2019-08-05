VENV=.venv

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

.PHONY: init-venv
init-venv:
	@echo "Start init-venv..."
	@command -v gettext >/dev/null 2>&1 ||sudo apt install gettext
	@test -d ${VENV} && echo "Virtual environment is exists." || python3 -m venv ${VENV}
	@. ${VENV}/bin/activate \
		&& echo "Installing python libraries..." \
		&& python3 -m pip install -q --upgrade pip \
		&& python3 -m pip install -q -r requirements.txt
	@echo "Finish init-venv"

.PHONY: update
update:
	@echo "Start update..."
	@. ${VENV}/bin/activate \
		&& python update.py
	@echo "Finish update"

.PHONY: build
build: update
	@echo "Start build..."
	@. ${VENV}/bin/activate \
		&& ./setup.py sdist bdist_wheel
	@echo "Finish build"

.PHONY: upload-test
upload-test: clean build
	@echo "Start upload-test..."
	@. ${VENV}/bin/activate \
		&& python -m twine upload \
			-u ${TWINE_USERNAME} \
			-p ${TWINE_PASSWORD} \
			--repository-url 'https://test.pypi.org/legacy/' \
			dist/*
	@echo "Finish upload-test"

.PHONY: upload-pypi
upload-pypi: clean build
	@echo "Start upload-pypi..."
	@. ${VENV}/bin/activate \
		&& set TWINE_USERNAME=${TWINE_USERNAME} \
		&& set TWINE_PASSWORD=${TWINE_PASSWORD} \
		&& python -m twine upload dist/*
	@echo "Finish upload-pypi"
