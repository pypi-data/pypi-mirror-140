from pathlib import Path
from setuptools import setup
from setuptools.extension import Extension

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='obsd_crypt',
    version='0.0.2',
    author='Aisha Tammy',
    author_email='aisha@bsd.ac',
    description=
    'Python interface to the OpenBSD functions crypt_checkpass and crypt_newhash',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bsd-ac/obsd_crypt',
    headers=['obsd_crypt.h'],
    ext_modules=[
        Extension('_obsd_crypt', ['obsd_crypt_wrap.c', 'obsd_crypt.c'])
    ],
    py_modules=['obsd_crypt'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX :: BSD :: OpenBSD'
    ])
