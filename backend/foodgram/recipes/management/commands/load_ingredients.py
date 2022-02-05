from django.core.management.base import BaseCommand

import json

from recipes.models import Ingredient



class Command(BaseCommand):
    help = 'Загружает в бд большой список ингредиентов'

    def handle(self, *args, **kwargs):
        path_for_file = './recipes/management/commands/ingredients.json'

        f = open(path_for_file, 'r')
        data = json.load(f)
        for i in data:
            Ingredient.objects.create(
                name=i['name'],
                measurement_unit=i['measurement_unit']
            )
        f.close()
