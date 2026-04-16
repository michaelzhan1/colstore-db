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

# generate test cases
generate-all-tests: # TODO: depend on files existing
	# TODO:

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
	rm -rf $(TEST_INPUT) $(TEST_EXPECTED)
