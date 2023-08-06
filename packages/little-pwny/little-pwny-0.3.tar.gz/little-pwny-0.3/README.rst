little-pwny
***********

Has my password been compromised? And how often?

|pypi-release|


`little-pwny` queries the `have-i-been-pwned password database
<https://haveibeenpwned.com/Passwords>`_ for breaches that contain a given
passphrase and returns the number of breaches found. It does *not* reveal the
plain passphrase to the HIBP server (nor to anyone/anything else, see below).

`little-pwny` works with plain Python 3.x and requires no additional packages.


Usage
=====

::

    $ pwny p@ssw0rd
    51763

    $ pwny aiPh1eehec8AhY2y
    0

Use::

    $ pwny --help

to learn more about all options supported.

Please note, that the Python package is called `little-pwny` while the
executable script is called `pwny`.

At no time the raw password is transferred to https://haveibeenpwned.com (or
elsewhere). Instead we use the generously offered haveibeenpwned.com-API to
deploy `k-anonymity <https://en.wikipedia.org/wiki/K-anonymity>`_. I.e. we send
the first five chars of the SHA1 hash of any given password. This way you can
check new passwords without revealing them to the server (or any other party).



Install
=======

You need at least some Python3 interpreter installed on your System.

with `pip`
----------

Simply::

    $ pip3 install --user little-pwny

Leave out `--user` if you are root and want to install `little-pwny`
system-wide.

If `pip` is not installed on your system, chances are, your Python3 comes with
`pip` included::

    $ python3 -m pip install --user little-pwny

(again you can leave `--user` out in case you are root).

If that fails as well, you might use your systems package manager to install
`pip3`. On Ubuntu for instance this will do::

    $ sudo apt install python3-pip
    $ sudo pip3 install little-pwny


From Source
-----------

Clone the source::

     $ git clone https://codeberg.org/ulif/little-pwny
     $ cd little-pwny

Create and activate a virtualenv::

     $ virtualenv venv
     $ source ./venv/bin/activate.sh

Then, from this directory, install the package::

     [venv] $ pip install -e .


Running Tests
=============

We use `tox` and `py.test` for testing. So,::

     $ pip install tox
     $ tox

should run all tests.


.. |pypi-release| image:: https://img.shields.io/pypi/v/little-pwny?color=006dad
   :target: https://pypi.python.org/pypi/little-pwny/
   :alt: Latest release
