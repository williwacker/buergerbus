# Generated by Django 2.2.2 on 2019-06-19 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Klienten', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orte',
            name='ort',
            field=models.CharField(max_length=50),
        ),
    ]
