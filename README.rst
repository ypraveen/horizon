======================================================================================
LBaaS SSL Certificate Upload and Association Support for Horizon (OpenStack Dashboard)
======================================================================================

This branch contains example code to upload SSL certificates to a specified
Avi Controller and to associate uploaded certificates with any VIP or Pool
created with LBaaS API.

* A new "Certificates" tab to upload certificates to the Avi Controller
* A new "Associate Certificates" link for each Pool that has a VIP associated with it and at least one of VIP or Pool protocols is "HTTPS".

Modify the openstack_dashboard/local/local_settings.py to include the
IP address of the Avi Controller. Example:
AVI_CONTROLLER_IP = "10.10.32.53"

=============================
Horizon (OpenStack Dashboard)
=============================

Horizon is a Django-based project aimed at providing a complete OpenStack
Dashboard along with an extensible framework for building new dashboards
from reusable components. The ``openstack_dashboard`` module is a reference
implementation of a Django site that uses the ``horizon`` app to provide
web-based interactions with the various OpenStack projects.

* Release management: https://launchpad.net/horizon
* Blueprints and feature specifications: https://blueprints.launchpad.net/horizon
* Issue tracking: https://bugs.launchpad.net/horizon


Using Horizon
=============

See ``doc/source/topics/install.rst`` about how to install Horizon
in your OpenStack setup. It describes the example steps and
has pointers for more detailed settings and configurations.

It is also available at http://docs.openstack.org/developer/horizon/topics/install.html.

Getting Started for Developers
==============================

``doc/source/quickstart.rst`` or
http://docs.openstack.org/developer/horizon/quickstart.html
describes how to setup Horizon development environment and start development.

Building Contributor Documentation
==================================

This documentation is written by contributors, for contributors.

The source is maintained in the ``doc/source`` directory using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/

* Building Automatically::

    $ ./run_tests.sh --docs

* Building Manually::

    $ tools/with_venv.sh sphinx-build doc/source doc/build/html

Results are in the ``doc/build/html`` directory
