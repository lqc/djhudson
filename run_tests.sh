#!/bin/sh

cd test_project
PYTHONPATH=.. python manage.py hudson2 django_hudson
