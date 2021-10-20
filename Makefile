lint:
	@flake8 research
	@mypy research

install:
	poetry install

run:
	python -m research.tools.cli --site ${site} --start ${start} --count ${count} --max-urls ${max-urls} --csv-file ${csv-file}