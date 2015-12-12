"""
A setuptools based setup module.
"""

# Always prefer setuptools over distutils
from setuptools import setup  # , find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = f.read()

# Get the version number from the VERSION file
# with open(path.join(here, 'VERSION')) as version_file:
#     version = version_file.read().strip()

setup(
	name='DEnM_Visualizer',
	version='1.0.2',
	description='TriKinetics Environnemental Monitor visualiser',
	long_description=long_description,
	url='https://github.com/samrund/DEnM_Visualizer',
	author='Marek Strelec',
	author_email='marek.strelec@gmail.com',
	license='MIT',

	# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
	],
	keywords='TriKinetics Monitor visualiser',

	packages=['denmonitor'],
	install_requires=['wxPython', 'matplotlib'],
	package_dir={'denmonitor': 'src/denmonitor'},
	scripts=['src/denmonitor/denmonitor.pyw'],
	entry_points={
		'console_scripts': [],
	},
)
