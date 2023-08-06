cijoe-pkg-spdk: cijoe testcases and testplans for SPDK
======================================================

.. image:: https://img.shields.io/pypi/v/cijoe-pkg-spdk.svg
   :target: https://pypi.org/project/cijoe-pkg-spdk
   :alt: PyPI

.. image:: https://github.com/refenv/cijoe-pkg-spdk/workflows/selftest/badge.svg
   :target: https://github.com/refenv/cijoe-pkg-spdk/actions
   :alt: Build Status

Install
=======

The package is distributed via PyPi, run the following to command to install:

.. code-block:: bash

  pip install --user cijoe-pkg-spdk

To install the development preview, install:

.. code-block:: bash

  pip install --user --pre cijoe-pkg-spdk

See the `Cijoe` for additional documentation.

If you find bugs or need help then feel free to submit an `Issue`_. If you want
to get involved head over to the `GitHub page`_ to get the source code and
submit a `Pull request`_ with your changes.

Test-target Environment
=======================

On the test-target, make sure you install::

  lshw
  screen
  time

Build FIO on the test-target::

  cd /opt/fio
  ./configure
  make

Build SPDK on the test-target::

  cd /opt/spdk
  ./configure --with-fio=/opt/fio
  make

.. _Cijoe: https://cijoe.readthedocs.io/
.. _GitHub page: https://github.com/refenv/cijoe-pkg-spdk
.. _Pull request: https://github.com/refenv/cijoe-pkg-spdk/pulls
.. _Issue: https://github.com/refenv/cijoe-pkg-spdk/issues
