# Generated by Django 2.2.3 on 2019-07-13 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Einsatztage', '0002_auto_20190709_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buerotag',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Einsatzmittel.Buero'),
        ),
        migrations.AlterField(
            model_name='fahrtag',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Einsatzmittel.Bus'),
        ),
    ]