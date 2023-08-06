from setuptools import setup
from setuptools.extension import Extension

setup(
    name='obsd_crypt',
    version='0.0.1',
    author='Aisha Tammy',
    author_email='aisha@bsd.ac',
    description=
    'Python interface to the OpenBSD functions crypt_checkpass and crypt_newhash',
    url='https://github.com/bsd-ac/obsd_crypt',
    headers=['obsd_crypt.h'],
    ext_modules=[
        Extension('_obsd_crypt', ['obsd_crypt_wrap.c', 'obsd_crypt.c'])
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX :: BSD :: OpenBSD'
    ])
