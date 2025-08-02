#!/bin/bash
# filepath: /home/niko/Programme/KURS/linux/install.sh

set -e

# Ins Hauptverzeichnis wechseln (ein Verzeichnis nach oben)
cd "$(dirname "$0")/.."

echo "Virtuelle Umgebung wird erstellt..."
python3.10 -m venv venv

echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

echo "pip, setuptools und wheel werden aktualisiert..."
pip install --upgrade pip setuptools wheel

echo "Abhängigkeiten werden installiert..."
pip install -r requirements/requirements_intel.txt

echo "Datenbankmigrationen werden durchgeführt..."
cd web
python manage.py migrate


#echo "Superuser kann jetzt erstellt werden (optional)..."
#python manage.py createsuperuser
python manage.py runserver 5468


echo "Fertig! Starte den Server mit:"
echo "cd web && source ../venv/bin/activate && python manage.py runserver"