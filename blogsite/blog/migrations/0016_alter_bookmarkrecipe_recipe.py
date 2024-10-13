# Generated by Django 5.1.1 on 2024-10-12 23:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0015_alter_recipe_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookmarkrecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="blog.recipe"
            ),
        ),
    ]
