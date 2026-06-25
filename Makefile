# mCytoMAP-core — reproducibility targets
.PHONY: reproduce test provenance verify clean help

help:
	@echo "make reproduce   - run reproduce_values.py (dependency-free)"
	@echo "make test        - run the assertion test-suite (needs pytest)"
	@echo "make provenance  - (re)write outputs/ : values + checksums"
	@echo "make verify      - reproduce, then confirm outputs/ match a fresh deterministic run"
	@echo "make clean       - remove caches"

reproduce:
	python3 reproduce_values.py

test:
	pytest -q

provenance:
	python3 provenance.py

verify: reproduce
	python3 provenance.py --check

clean:
	rm -rf __pycache__ tests/__pycache__ .pytest_cache *.egg-info build dist
