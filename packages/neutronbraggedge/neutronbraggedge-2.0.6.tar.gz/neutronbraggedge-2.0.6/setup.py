#!/usr/bin/env python
from setuptools import setup, find_packages
import neutronbraggedge

VERSION = neutronbraggedge.__version__

setup(
    name = "neutronbraggedge",
    version = VERSION,
    author = "Jean Bilheux",
    author_email = "bilheuxjm@ornl.gov", 
    packages = find_packages(exclude=['tests', 'notebooks']),
    package_data = { 'neutronbraggedge' : ['data/material_list.dat', 
                                           'data/full_material_list.dat']},
    include_package_data = True,
    data_files = [('neutronbraggedge', ['neutronbraggedge/config.cfg']),
                  #('neutronbraggedge/data', ['neutronbraggedge/data/material_list.dat'])
                  ],
    test_suite = 'tests',
    install_requires = [
        'numpy',
        'configparser',
        'pandas',
        'lxml',
        'html5lib',
        'beautifulsoup4',
    ],
    dependency_links = [
    ],
    description = "Bragg Edge work at the SNS",
    license = 'BSD',
    keywords = "neutron imaging bragg edge",
    url = "https://github.com/ornlneutronimaging/BraggEdge",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'],
    # download_url = '',
)


# End of file
