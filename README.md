# praktikum_new_diplom

Чтобы собрать проект надо выполнить следующие команды:
```
cd backend/
```
```
python -m venv venv
```
```
source venv/Scripts/activate
```
```
pip install -r requirements.txt
```
```
python manage.py makemigrations
```
```
python manage.py migrate
```
```
python manage.py fill_db
```
После каждого запуска API тестов можно сбрасывать пользователей из директрии postman-collection командой (c активированным виртуальным оркужением):
```
bash clear_db.sh
```