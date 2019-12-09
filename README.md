# buergerbus
Application for the management of driving services

Installation

source activate

python manage.py migrate

python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic

python manage.py loaddata Einsatzmittel/fixtures/wochentage.json

python manage.py loaddata Einsatzmittel/fixtures/busse.json

python manage.py loaddata Einsatzmittel/fixtures/bueros.json

python schreibe_strassennamen.py

python schreibe_dienstleister.py

python manage.py createsuperuser










