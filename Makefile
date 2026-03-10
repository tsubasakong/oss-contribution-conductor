.PHONY: test validate package

test:
	python3 tests/run_all.py

validate:
	python3 tools/validate_repo.py
	python3 -m py_compile oss-contribution-conductor/scripts/*.py tools/*.py tests/*.py
	python3 tests/run_all.py

package:
	python3 tools/package_skill.py
