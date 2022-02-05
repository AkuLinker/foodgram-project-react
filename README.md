# foodgram
### Ссылка
http://foodgram.akulinker.ru
### админ
логин: admin1\
пароль: admin1
### Описание
Сервис для публикации рецептов, их отслеживания и составления списка покупок. 
### Технологии
- Python
- Django
- Django REST framework
- Docker
### Для запуска в папке /infa нужно выполнить
```
docker-compose up
```
### После запуска проекта нужно выполнить
```
docker-compose exec backend python manage.py migrate
```
```
docker-compose exec backend python manage.py collectstatic
```
### Для заполнения бд ингредиентами нужно выполнить
```
docker-compose exec backend python manage.py load_ingredients
```
### Автор
- [Иван](https://github.com/AkuLinker/ "GitHub аккаунт")
