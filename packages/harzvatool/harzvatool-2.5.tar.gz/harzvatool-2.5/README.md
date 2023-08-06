
[harzvatool](https://github.com/Harzva/harzvatool/)
torch and will requirement no need to have torch
to write your content.

python setup.py sdist bdist_wheel  

python -m twine upload dist/*

python -m twine upload --repository testpypi dist/*

