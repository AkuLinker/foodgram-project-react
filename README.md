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
docker-compose exec backend python manage.py shell
```
```
from recipes.models import Ingredient
```
```
from recipes.ingredients_import import import_ingredient
```
```
import_ingredient('./recipes/ingredients.json', Ingredient)
```
```
exit()
```
### Автор
- [Иван](https://github.com/AkuLinker/ "GitHub аккаунт")
