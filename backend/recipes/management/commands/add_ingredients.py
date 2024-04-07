import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Наполнение БД ингредиентоами из ingredients.json'

    def handle(self, *args, **kwargs):
        with open('recipes/data/ingredients.json', 'r', encoding='utf-8') as file:
            ingredients_data = json.load(file)
        for ingredient_data in ingredients_data:
            try:
                ingredient = Ingredients.objects.get(
                    name=ingredient_data['name']
                )
                self.stdout.write(self.style.WARNING(
                    f'Ингредиент {ingredient.name} уже есть в БД'
                ))
            except Ingredients.DoesNotExist:
                ingredient = Ingredients.objects.create(
                    name=ingredient_data['name'],
                    measurement_unit=ingredient_data['measurement_unit']
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Added ingredient: {ingredient.name}'
                ))
