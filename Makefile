.DEFAULT_GOAL := help

SHELL = bash -o pipefail

# Color for shell text
YELLOW := \033[0;93m
NO_COLOR := \033[0m

# Folders for end-to-end tests
TEST_ENV_DIR = tests/venv
TEST_OUTPUT_DIR = tests/output


# Initialisation

.PHONY: init
init:  ## Bootstrap for local development
	poetry install
	poetry run pre-commit install

# Build

.PHONY: build
build: init schemas  # Build package
	rm -rf dist
	poetry build -vvv

# Tests

.PHONY: test
test: init test-unit test-e2e  ## Launch all the test tasks (unit, end-to-end)

.PHONY: test-unit
test-unit: build ## Launch unit tests
	poetry run pytest --cov $(PYTEST_ARGS)

.PHONY: test-e2e
test-e2e: prepare-test-env  ## Launch end-to-end tests
	$(MAKE) test-e2e-case CASE=1_initial_immovable_properties TIMESTAMP=2025-01-31T12:05:56.084
	$(MAKE) test-e2e-case CASE=2_initial_sale_of_goods TIMESTAMP=2025-01-25T12:55:02.003
	$(MAKE) test-e2e-case CASE=3_additional TIMESTAMP=2025-01-25T14:17:22.241
	$(MAKE) test-e2e-case CASE=4_corrective TIMESTAMP=2025-01-28T08:12:00.003
	$(MAKE) test-e2e-case CASE=5_initial_assuming TIMESTAMP=2025-01-30T21:48:22.209
	$(MAKE) test-e2e-case CASE=6_initial_assumed TIMESTAMP=2025-01-16T11:22:59.456


.PHONY: test-e2e-case
test-e2e-case:
	@echo -e "$(YELLOW)$(CASE)$(NO_COLOR)"
	mkdir -p $(TEST_OUTPUT_DIR)/$(CASE)
	env DAC7=$(TEST_ENV_DIR)/bin/dac7 \
		ENV=PROD \
		TIMESTAMP=$(TIMESTAMP) \
		PLATFORM_JSON=$(wildcard examples/$(CASE)/input/platform_operator.json) \
		ENTITY_SELLERS_JSON=$(wildcard examples/$(CASE)/input/entity_sellers.json) \
		OTHERS_JSON=$(wildcard examples/$(CASE)/input/other_platform_operators.json) \
		INDIVIDUAL_SELLERS_JSON=$(wildcard examples/$(CASE)/input/individual_sellers.json) \
		OUTPUT_DIR=$(TEST_OUTPUT_DIR)/$(CASE) \
		bash cli/tests/scripts/build_file.sh
	cat $(TEST_OUTPUT_DIR)/$(CASE)/*.xml | cmp examples/$(CASE)/declaration.xml -


.PHONY: prepare-test-env
prepare-test-env: build
	@echo -e "$(YELLOW)Preparting tests$(NO_COLOR)"
	rm -rf $(TEST_ENV_DIR)
	poetry run virtualenv $(TEST_ENV_DIR)
	$(TEST_ENV_DIR)/bin/pip install dist/*.whl
	rm -rf $(TEST_OUTPUT_DIR)
	mkdir -p $(TEST_OUTPUT_DIR)


# Schema export, both JSON and XSD

.PHONY: schemas
schemas: schemas-xsd schemas-json

.PHONY: schemas-xsd
schemas-xsd: cli/src/dac7/schemas/DPIXML_v1.1-fr1.xsd cli/src/dac7/schemas/isodpitypes_v1.0-fr1.xsd cli/src/dac7/schemas/oecddpitypes_v1.0-fr1.xsd

cli/src/dac7/schemas/%.xsd: schemas/xml/%.xsd
	mkdir -p cli/src/dac7/schemas
	cp $< $@

.PHONY: schemas-json
schemas-json:
	poetry run dac7 schemas json2xml > schemas/json/DPIXML_v1.1-fr1.json
	poetry run dac7 schemas build platform-operator > schemas/json/partial/platform_operator.json
	poetry run dac7 schemas build other-platform-operators > schemas/json/partial/other_platform_operators.json
	poetry run dac7 schemas build entity-sellers > schemas/json/partial/entity_sellers.json
	poetry run dac7 schemas build individual-sellers > schemas/json/partial/individual_sellers.json

# Implements this pattern for autodocumenting Makefiles:
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
#
# Picks up all comments that start with a ## and are at the end of a target definition line.
.PHONY: help
help:  ## List the available make target with their description
	@grep -E '^[a-zA-Z0-9_%.-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
