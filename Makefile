upload_to_pip:
	rm -rf ./dist
	rm -rf ./build
	python3 setup.py sdist bdist_wheel
	twine upload dist/*


.PHONY: test