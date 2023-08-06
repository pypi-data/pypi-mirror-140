
===============================
Satellite-Constellation-Creator
===============================


.. image:: https://img.shields.io/pypi/v/satellite-constellation.svg
    :target: https://pypi.python.org/pypi/satellite-constellation

.. image:: https://img.shields.io/travis/SaberAidan/SatelliteConstellationCreator.svg
    :target: https://travis-ci.org/SaberAidan/SatelliteConstellationCreator


Library for representing satellite constellations and ground stations


Installation
-------------
To install latest released version::

    pip install satellite-constellation


To install from github master branch::

    pip install https://gitlab.com/open-galactic/satellite-constellation.git


For development::

    # fork https://gitlab.com/open-galactic/satellite-constellation.git to YOUR_GITLAB
    # clone your repo locally
    git clone https://YOUR_GITLAB@gitlab.com/YOUR_GITLAB/satellite-constellation.git
    cd SatelliteConstellationCreator

    # add upstream remote
    git remote add upstream https://gitlab.com/open-galactic/satellite-constellation.git

    # create a virtualenv
    python3 -m venv .venv
    source .venv/bin/activate

    # install for development
    pip install -r requirements.txt

Testing if installation is good::
    $ satellite-constellation --test

Features
--------

JSON serialisable orbital elements for satellite constellation creation. Individual Satellite element creation class.


Credits
-------

This package is a conversion of existing academic Matlab code created by Saber Astronautics Australia Pty. Ltd. for use in creating scenes in the Predictive Interactive Ground Interface software.
