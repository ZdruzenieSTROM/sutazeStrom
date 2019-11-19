@echo off

rem Nastav kódovanie na UTF-8
chcp 65001

title Inicializácia

SET ENV_NAME=sutazestrom-env

rem Choď do priečinka v ktorom je skript
cd %~dp0

rem Vytvor a aktivuj prostredie pre python
py -m venv %ENV_NAME%
call %ENV_NAME%\Scripts\activate.bat

rem Nainštaluj balíky
pip install -r requirements.txt

rem Inicializuj Django
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'gumibanan')"

rem Deaktivuj prostredie pre python
call %ENV_NAME%\Scripts\deactivate.bat

rem Vytvor skript na spustenie serveru
echo chcp 65001> run.bat
echo.>> run.bat
echo title Odovzdávač>> run.bat
echo.>> run.bat
echo call %ENV_NAME%\Scripts\activate.bat>> run.bat
echo.>> run.bat
echo python manage.py runserver 0.0.0.0:8000>> run.bat
echo.>> run.bat
echo call %ENV_NAME\Scripts\deactivate.bat>> run.bat

rem Spusti server
call run.bat
