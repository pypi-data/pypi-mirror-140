# What it has
Helpers I use for Data Science projects

# Additional info
* https://pypi.org/project/blp-helpers-data-science/
* https://github.com/leugh/helpers_data_science
# How to use it
```python pip install blp-helpers-data-science```

# How to develop it
1. Ensure setuptools is installed: ```pip install --user --upgrade setuptools wheel```
2. Ensure twine is installed ```pip install --user --upgrade twine```
3. Make changes
4. Update CHANGELOG.md
5. Update setup.py
7. Create distribution packages ```python setup.py sdist bdist_wheel```
5. Upload to pypi ```python -m twine upload dist/*```
> Source: https://widdowquinn.github.io/coding/update-pypi-package/
