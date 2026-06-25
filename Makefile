# mCytoMAP-core — reproducibility targets
.PHONY: reproduce test provenance diff-output verify docker-reproduce clean help

help:
	@echo "make reproduce         - run reproduce_values.py (dependency-free)"
	@echo "make test              - run the assertion test-suite (needs pytest)"
	@echo "make provenance        - (re)write outputs/ : values + checksums"
	@echo "make diff-output       - confirm console output matches the committed transcript"
	@echo "make verify            - reproduce + diff-output + provenance --check (full audit)"
	@echo "make docker-reproduce  - build the pinned container and reproduce inside it"
	@echo "make clean             - remove caches"

reproduce:
	python3 reproduce_values.py

test:
	pytest -q

provenance:
	python3 provenance.py

diff-output:
	python3 reproduce_values.py | diff -u outputs/expected_console_output.txt -

verify: reproduce diff-output
	python3 provenance.py --check

docker-reproduce:
	docker build -t mcytomap-core .
	docker run --rm mcytomap-core

clean:
	rm -rf __pycache__ tests/__pycache__ .pytest_cache *.egg-info build dist
