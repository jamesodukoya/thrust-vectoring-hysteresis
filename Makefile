.PHONY: figures test
figures:
	python3 -m tvh.figures
test:
	python3 -m pytest tests -q
