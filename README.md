# Продуктовый помощник Foodgram

[![example workflow](https://github.com/anton988/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/anton988/foodgram-project-react/actions/workflows/main.yml)

Продуктовый помощник Foodgram - это сервис, с помощью которого пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 

Для работы проекта был разработан и настроен CI/CD.

### Технологии проекта:
- Python
- Django
- Django REST framework
- Postgres
- Docker
- Nginx
- GitHub Actions

### Как запустить проект:
1. Клонировать репозиторий:
`git clone https://github.com/anton988/foodgram-project-react`
2. Установите Docker на сервере:
sudo apt install docker.io
3. Установите Docker-compose на сервере:
```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
4. Скопируйте файл `docker-compose.production.yaml` на сервер:
`scp docker-compose.yaml <username>@<host>:/home/<username>/`
5. После успешного деплоя зайдите на боевой сервер и выполните команды:
```
sudo -f docker-compose.production.yml up -d
```
```
sudo -f docker-compose.production.yml exec backend python manage.py migrate # примените миграции
```
```
sudo -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input # подгрузите статику
```
```
sudo -f docker-compose.production.yml exec backend python manage.py load_data # загрузите моковые данные
```
```
sudo -f docker-compose.production.yml exec backend python manage.py createsuperuser # создайте суперпользователя
```
### Автор
[Антон Титков](https://github.com/anton988)