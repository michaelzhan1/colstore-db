TEST_DATA = tests/data
TEST_INPUT = tests/input
TEST_OUTPUT = tests/output
TEST_EXPECTED = tests/expected

build:
	$(MAKE) -C src

build-image:
	docker build --tag=colstore-db .

# down not needed due to --rm
up:
	docker container run \
		--name db \
		--rm \
		-it \
		-v ./src:/app/src \
		-v ./tests:/app/tests \
		-v ./Makefile:/app/Makefile \
		colstore-db \
		/bin/bash

prep-tests:
	[ -d $(TEST_DATA) ] || mkdir -p $(TEST_DATA)
	[ -d $(TEST_INPUT) ] || mkdir -p $(TEST_INPUT)
	[ -d $(TEST_EXPECTED) ] || mkdir -p $(TEST_EXPECTED)

# generate test cases
generate-tests: prep-tests
	python3 tests/scripts/milestone1.py
	python3 tests/scripts/milestone2.py
	python3 tests/scripts/milestone3.py
	python3 tests/scripts/milestone4.py

# run tests with optional `mile` variable
# TODO: add specific test number as well: mile -> mile_id, test_id?
test:
	@if [ -z "$(mile)" ]; then \
		echo "TODO: running all tests"; \
	elif ! echo "$(mile)" | grep -Eq '^[1-5]$$'; then \
		echo "Invalid 'mile', must be between 1 and 5"; exit 1; \
	else \
		echo "TODO: specific test"; \
	fi

clean:
	$(MAKE) -C src clean

clean-tests:
	rm -rf $(TEST_DATA) $(TEST_INPUT) $(TEST_EXPECTED)

.PHONY: build test