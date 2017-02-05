

upload:
	python setup.py sdist bdist_wheel upload -r pypi

register:
	python setup.py register -r pypi
