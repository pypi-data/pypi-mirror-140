from setuptools import setup
from pathlib import Path
from package_list import packages as _packages
long_description = Path("./README.md").read_text()

setup(
  name='jft',
  version='0.0.28',
  license='MIT',
  description='Function Test Pair Toolbox',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='@JohnRForbes',
  author_email='john.robert.forbes@gmail.com',
  url='https://gitlab.com/zereiji/jft',
  packages=_packages,
  keywords='jft',
  install_requires=[],
)
