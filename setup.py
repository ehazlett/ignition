#!/usr/bin/env python

from distutils.core import setup

setup(name='ignition',
    version = '0.1',
    author = 'Evan Hazlett',
    author_email = 'ejhazlett@gmail.com',
    packages = ['ignition'],
    description = 'Python web application stack creator',
    url = 'https://github.com/ehazlett/ignition',
    license = 'License :: OSI Approved :: Apache Software License',
    long_description = """
    Ignition will create a Python web application stack including the Python project
    (currently Django only), uWSGI config, and Nginx config, along with
    startup and shutdown scripts.""",
    scripts = ['ignite.py'],
    platforms = [
        "All",
        ],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        ]
    )

