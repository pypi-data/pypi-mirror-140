
econpizza
=========

.. image:: https://badge.fury.io/py/econpizza.svg
    :target: https://badge.fury.io/py/econpizza

Contains tools to simulate nonlinear perfect foresight models. The baseline mechanism is a Fair-Taylor-like stacking method similar to the nonlinear solver in dynare, but faster and more robust.

The package makes heavy use of `automatic differentiation <https://en.wikipedia.org/wiki/Automatic_differentiation>`_ via `jax <https://jax.readthedocs.io/en/latest/notebooks/quickstart.html>`_!

Installation
-------------

It's as simple as:

.. code-block:: bash

   pip install econpizza

Documentation
-------------

There is some `documentation <https://econpizza.readthedocs.io/en/latest/index.html>`_ out there.


Citation
--------

**econpizza** is developed by Gregor Boehl to simulate nonlinear perfect foresight models. Please cite it with

.. code-block::

    @techreport{boehl2021rational,
    title         = {Rational vs. Irrational Beliefs in a Complex World},
    author        = {Boehl, Gregor and Hommes, Cars},
    year          = 2021,
    institution   = {IMFS Working Paper Series}
    }


I appreciate citations for **econpizza** because it helps me to find out how people have been using the package and it motivates further work.


References
----------

Boehl, Gregor and Hommes, Cars (2021). `Rational vs. Irrational Beliefs in a Complex World <https://gregorboehl.com/live/rational_chaos_bh.pdf>`_. *IMFS Working papers*
