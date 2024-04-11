# praktikum_new_diplom

Чтобы все работла надо выполнить следующие команды:

cd backend/
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py fill_db