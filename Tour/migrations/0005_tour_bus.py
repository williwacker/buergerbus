# Generated by Django 2.2.2 on 2019-06-19 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Bus', '0002_auto_20190619_1416'),
        ('Tour', '0004_auto_20190619_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='bus',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='Bus.Bus'),
            preserve_default=False,
        ),
    ]
