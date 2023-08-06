.PHONY: default clean install pip-install generate env-check-% test install-with-tests sanity-check
.SILENT: generate # Prevent echoing of any tokens

PACKAGE_NAME=pycarlo
ENVIRONMENT_NAME=venv
MCD_URL=https://api.getmontecarlo.com/graphql

# Schema generator util
SCHEMA_GEN_UTIL=utils/generate.py

# Generated schema destinations
SCHEMA_FROM_INTROSPECTION=pycarlo/lib/schema.json
SCHEMA_PY=$(PACKAGE_NAME)/lib/schema.py

default:
	@echo "Read the readme"

clean:
	rm -rf $(ENVIRONMENT_NAME) build dist $(PACKAGE_NAME).egg-info .coverage nosetests.xml

pip-install:
	pip install --editable .

install: clean
	virtualenv $(ENVIRONMENT_NAME); \
	. $(ENVIRONMENT_NAME)/bin/activate; \
	pip install -r requirements-dev.txt; \
	$(MAKE) pip-install; \
	pip show $(PACKAGE_NAME)

sanity-check:
	@# Requires activating the virtualenv created in `install` if running locally.
	@# Checks basic functionality of the SDK (e.g. after auto-generating from introspection).
	@python -c "from pycarlo.core import Client, Query; client = Client(); query = Query();\
		query.get_user.__fields__('first_name'); print(f'Norman\'s on sabbatical, {client(query).get_user.first_name}!')"

generate: install env-check-MCD_DEFAULT_API_ID env-check-MCD_DEFAULT_API_TOKEN
	# Generate sgqlc.types from introspection.
	# Requires exporting API ID/Secret before usage.
	echo "Retrieving latest schema."; \
	. $(ENVIRONMENT_NAME)/bin/activate; \
	python $(SCHEMA_GEN_UTIL) --header 'x-mcd-id:${MCD_DEFAULT_API_ID}' --header 'x-mcd-token:${MCD_DEFAULT_API_TOKEN}' $(MCD_URL) $(SCHEMA_FROM_INTROSPECTION); \
	echo "Generating types."; \
	sgqlc-codegen schema --docstrings $(SCHEMA_FROM_INTROSPECTION) $(SCHEMA_PY) ; \
	echo "Executing sanity check."; \
	$(MAKE) sanity-check; \
	echo "Done! Have a nice day."; \

test:
	@# Requires activating the virtualenv created in `install` if running locally.
	export DEBUG=True; nosetests ./tests --with-coverage --cover-package=$(PACKAGE_NAME) --with-xunit

install-with-tests: install
	. $(ENVIRONMENT_NAME)/bin/activate; $(MAKE) test

distribute: install
	. $(ENVIRONMENT_NAME)/bin/activate; \
	pip install -r requirements-ci.txt; \
	python setup.py sdist bdist_wheel; \
	twine check dist/*; \
	twine upload --non-interactive dist/*

env-check-%:
	@if [ -z '${${*}}' ]; then echo 'Missing expected env variable of "$*".' && exit 1; fi
