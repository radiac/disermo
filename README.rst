=======
Disermo
=======

Self hosted server monitoring.


Installation
============

This requires Python 3.7.

During development, install in a virtual environment::

    mkdir disermo
    cd disermo
    git clone <path-to-repo> repo
    virtualenv --python=python3.7 venv
    . venv/bin/activate
    pip install pip-tools
    cd repo
    pip-sync


Quickstart
==========

Create a Disermo script based on ``example.py``.

To run it::

    /path/to/venv/bin/python /path/to/repo/example.py


To run tests::

    cd disermo/repo
    . ../venv/bin/activate
    pytest --flake8 --mypy --cov=disermo --cov-report=term --cov-report=html
