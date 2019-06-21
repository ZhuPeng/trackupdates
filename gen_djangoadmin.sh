# remove previous django admin
rm -rf djangoadmin
django-admin startproject djangoadmin
cd djangoadmin/
ls
ls djangoadmin/
django-admin.py startapp trackup

# replace db TODO: specified db name from yaml
sed -i "" 's/db.sqlite3/..\/db.sqlite3/g' djangoadmin/settings.py

# add trackupdates to Install apps
sed -i "" "s/'django.contrib.staticfiles',/'django.contrib.staticfiles', 'trackup',/g" djangoadmin/settings.py

# auto-genenerate models.py
python manage.py inspectdb > trackup/models.py 

# register models
echo '
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.apps import apps

# Register your models here.

app_models = apps.get_app_config("trackup").get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
' > trackup/admin.py
cat trackup/admin.py

python manage.py clearsessions
python manage.py makemigrations --empty trackup
python manage.py makemigrations trackup
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# create auth user to access django admin
# python manage.py createsuperuser
