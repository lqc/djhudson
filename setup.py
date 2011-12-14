#!/usr/bin/env python
# -*- coding: utf-8

from setuptools import setup, find_packages

setup(
    name='djhudson',
    version='0.5.0a4',
    author=u'Łukasz Rekucki',
    author_email='lrekucki@gmail.com',
    description='Plug and play continuous integration with django and hudson',
    license='LGPL',
    platforms=['Any'],
    keywords=['unittest', 'testrunner', 'hudson', 'django'],
    url='http://github.com/lqc/djhudson',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Framework :: Django',
        'Framework :: Django :: 1.3',
    ],
    packages=[
        'djhudson',
        'djhudson.management',
        'djhudson.management.commands',
        'djhudson.plugins',
        'djhudson.runners',
    ],
#     package_data={'djhudson': ['management/commands/pylint.rc']},
    zip_safe=False,
    include_package_data=True
)
