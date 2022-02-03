# foodgram
### Ссылка
Пока нет
### Описание
Сервис для публикации рецептов, их отслеживания и составления списка покупок. 
### Технологии
- Python
- Django
- Django REST framework
- Docker
### Для запуска в папке /infa нужно выполнить
```
docker compose up
```
### После запуска проекта нужно выполнить
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic
```
### Автор
- [Иван](https://github.com/AkuLinker/ "GitHub аккаунт")