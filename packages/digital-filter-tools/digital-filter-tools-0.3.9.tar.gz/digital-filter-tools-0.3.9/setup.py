# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='digital-filter-tools',
    version='0.3.9',
    py_modules=['digital_filter_tools'],
    install_requires=['numpy', 'matplotlib', 'ac-electricity'],
    description='An educational module about digital filters',
    author='Fabrice Sincère',
    author_email='fabrice.sincere@ac-grenoble.fr',
    maintainer='Fabrice Sincère',
    maintainer_email='fabrice.sincere@ac-grenoble.fr',
    url='https://framagit.org/fsincere/digital-filter-tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: French",
    ],
    python_requires='>=3',)
