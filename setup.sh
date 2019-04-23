#!/bin/bash

ENV_NAME=sutazestrom

cd $(dirname $0)

python3 -m virtualenv $ENV_NAME --python=$(which python3)
source $ENV_NAME/bin/activate

pip3 install -r requirements.txt

python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'gumibanan')"

deactivate

echo -e "#!/bin/bash\n\ncd \$(dirname \$0)\nsource $ENV_NAME/bin/activate\npython3 manage.py runserver 0:8000\ndeactivate\n" > run.sh
chmod +x run.sh

source run.sh
