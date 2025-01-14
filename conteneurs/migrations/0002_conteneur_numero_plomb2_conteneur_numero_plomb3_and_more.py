# Generated by Django 5.1 on 2024-12-17 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conteneurs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conteneur',
            name='numero_plomb2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='conteneur',
            name='numero_plomb3',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='conteneur',
            name='photo_plomb2',
            field=models.ImageField(blank=True, null=True, upload_to='photos_plomb2/'),
        ),
        migrations.AddField(
            model_name='conteneur',
            name='photo_plomb3',
            field=models.ImageField(blank=True, null=True, upload_to='photos_plomb3/'),
        ),
        migrations.DeleteModel(
            name='IsoTanks',
        ),
    ]
