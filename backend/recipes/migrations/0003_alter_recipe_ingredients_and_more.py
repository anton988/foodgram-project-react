# Generated by Django 5.0.3 on 2024-04-08 08:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipe_ingredients', through='recipes.RecipeIngredients', to='recipes.ingredients', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipeingredients_ingredients', to='recipes.ingredients', verbose_name='Ингридиент'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipeingredients_recipe', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]
