#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
# ESTO RESETEA LA DB PARA ELIMINAR EL ERROR 500
python manage.py migrate --run-syncdb 
