#!/usr/bin/env python2


# This script needs python-distutils-extra, an extension to the standard
# distutils which provides i18n, icon support, etc.
# https://launchpad.net/python-distutils-extra

from glob import glob
from distutils.version import StrictVersion

try:
    import DistUtilsExtra.auto
except ImportError:
    import sys
    print >> sys.stderr, 'To build DBR you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)

assert StrictVersion(DistUtilsExtra.auto.__version__) >= '2.4', 'needs DistUtilsExtra.auto >= 2.4'

DistUtilsExtra.auto.setup(
    name='dbr',
    version='0.1.2',
    description='Daisy Book Reader',
    url='https://dbr.sourceforge.net',
    license='GPL v2 or later',
    author='Francisco Javier Dorado',
    author_email='javier@tiflolinux.org',

    data_files = [
    ('share/applications', ['dbr/dbr.desktop'])],
    scripts = ['scripts/dbr']


)
