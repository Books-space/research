lint:
	@flake8 research
	@mypy research

run:
	python -m research.tools.cli --site ${site} --start ${start} --count ${count} --max-urls ${max-urls} --csv-file ${csv-file}