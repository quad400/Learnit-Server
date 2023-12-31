# Generated by Django 4.1.5 on 2023-07-15 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_alter_course_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logoIcon', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('homeBackgroundImg', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('bannerImg', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('rev1', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('rev2', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('rev3', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('errorImg', models.ImageField(blank=True, null=True, upload_to='settings/')),
            ],
        ),
    ]
