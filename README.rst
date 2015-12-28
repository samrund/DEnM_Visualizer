|Logo|

DEnM-Visualizer
===============

|PyPi Status|


.. contents:: Table of contents
   :backlinks: top
   :local:

Dependencies
------------

- python 2.7
- matplotlib
- wxPython

Installation on Mac OS X
------------------------

matpotlib
~~~~~~~~~

One convenient way to install matplotlib with other useful Python software is to use one of the Python scientific software collections:

- `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ from Continuum Analytics
- `Canopy <https://enthought.com/products/canopy/>`_ from Enthought


If you are using recent Python 2.7 from `<http://www.python.org>`_, Macports or Homebrew, then you can use the standard pip installer to install matplotlib binaries in the form of wheels.

.. code:: sh

   pip install matplotlib


wxPython
~~~~~~~~

If you are using Anaconda, wxPython can be installed with

.. code:: sh

   conda install -c https://conda.anaconda.org/anaconda wxpython

For standard Python installations, wxPython can be downloaded from `<http://www.wxpython.org/download.php#osx>`_


DEnM-Visualizer
~~~~~~~~~~~~~~~

Similarly, DEnM-Visualizer can be easily installed using pip.

.. code:: sh

   pip install DEnM-Visualizer


Installation on Windows
-----------------------

matpotlib
~~~~~~~~~

If you don't already have Python installed, we recommend using
one of the `scipy-stack compatible Python distributions
<http://www.scipy.org/install.html>`_ such as WinPython, Python(x,y),
Enthought Canopy, or Continuum Anaconda, which have matplotlib and
many of its dependencies, plus other useful packages, preinstalled.

For standard Python installations you will also need to install compatible versions of *setuptools*, *numpy*, *python-dateutil*, *pytz*, *pyparsing*, and *cycler* in addition to matplotlib. In case Python 2.7 is not installed for all users (not the default), the Microsoft Visual C++ 2008 redistributable packages need to be installed.

wxpython
~~~~~~~~

If you are using Anaconda, wxPython can be installed with

.. code:: sh

   conda install -c https://conda.anaconda.org/anaconda wxpython

For standard Python installations, wxPython can be downloaded from `<http://www.wxpython.org/download.php#msw>`_



DEnM-Visualizer
~~~~~~~~~~~~~~~

Finally, DEnM-Visualizer can be easily installed using pip.

.. code:: sh

   pip install DEnM-Visualizer


Authors
-------

- Marek Strelec
- Samuel Rund


License
-------


See the `LICENSE <LICENSE.txt>`_ file for license rights and limitations (MIT).


.. |Logo| image:: https://raw.githubusercontent.com/samrund/DEnM_Visualizer/master/logo.png
.. |PyPi Status| image:: https://img.shields.io/pypi/v/tqdm.svg
   :target: https://pypi.python.org/pypi/DEnM-Visualizer


