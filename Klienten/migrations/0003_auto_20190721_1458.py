# Generated by Django 2.2.3 on 2019-07-21 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Klienten', '0002_klientenbus'),
    ]

    operations = [
        migrations.DeleteModel(
            name='KlientenBus',
        ),
        migrations.AddField(
            model_name='klienten',
            name='bus_id',
            field=models.IntegerField(blank=True, default=4, null=True),
        ),
    ]
