# Generated by Django 2.2.3 on 2019-07-09 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Einsatzmittel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buero',
            name='id',
        ),
        migrations.AlterField(
            model_name='buero',
            name='buero',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
    ]