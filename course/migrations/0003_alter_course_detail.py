# Generated by Django 4.1.5 on 2023-07-14 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_remove_category_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='detail',
            field=models.TextField(blank=True),
        ),
    ]