#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import codecs
import re

# Copied from wheel package
# here = os.path.abspath(os.path.dirname(__file__))
# #README = codecs.open(os.path.join(here, 'README.txt'), encoding='utf8').read()
# #CHANGES = codecs.open(os.path.join(here, 'CHANGES.txt'), encoding='utf8').read()

with codecs.open(os.path.join(os.path.dirname(__file__), 'graphform.py'),
                 encoding='utf8') as version_file:
    metadata = dict(
        re.findall(
            r"""__([a-z]+)__ = "([^"]+)""",
            version_file.read()))

print(metadata)

long_desc = "".join(open("README.md").readlines())

with open("requirements.txt") as f:
    requires = [x.strip() for x in f.readlines()]

setup(name='GraphForm',
      python_requires='>=3.6',
      version=metadata['version'],
      description='Recover the 3D structure from a graph.',
      long_description=long_desc,
      long_description_content_type="text/markdown",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.6",
      ],
      author='Masakazu Matsumoto',
      author_email='vitroid@gmail.com',
      url='https://github.com/vitroid/GraphForm/',
      keywords=['genice2', ],
      license='MIT',
      packages=find_packages(),
      install_requires=requires,
      py_modules=['graphform'],
            )
