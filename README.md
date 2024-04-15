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

Что не работает:
1. Фильтрация по избранному и корзине
2. Удаление из избранного и из корзины
3. Подписки