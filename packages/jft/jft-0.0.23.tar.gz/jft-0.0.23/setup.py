from setuptools import setup
from setuptools import find_packages
from pathlib import Path
long_description = Path("./README.md").read_text()

setup(
  name='jft',
  version='0.0.23',
  license='MIT',
  description='Function Test Pair Toolbox',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='@JohnRForbes',
  author_email='john.robert.forbes@gmail.com',
  url='https://gitlab.com/zereiji/jft',
  packages=['jft'],
  # packages=find_packages(where="jft"),
  keywords='jft',
  install_requires=[],
)
