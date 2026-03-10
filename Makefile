.PHONY: validate package

validate:
	python3 tools/validate_repo.py
	python3 -m py_compile oss-contribution-conductor/scripts/*.py tools/*.py

package:
	python3 tools/package_skill.py
