#!/usr/bin/env python
# -*- coding: utf-8

from setuptools import setup, find_packages

setup(
    name='djhudson',
    version='0.2',
    author='Łukasz Rekucki',
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
        'Topic :: Software Development :: Testing'
        'Framework :: Django',
        'Framework :: Django :: 1.3',
    ],
    packages=['django_hudson', 'django_hudson.management', 'django_hudson.management.commands', 'django_hudson.plugins', 'django_hudson.runners'],
#     package_data={'django_hudson': ['management/commands/pylint.rc']},
    zip_safe=False,
    include_package_data=True
)
