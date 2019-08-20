# Generated by Django 2.2.3 on 2019-07-24 14:37

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('Tour', '0005_auto_20190724_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='bus1',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='klient', chained_model_field='name', null=True, on_delete=django.db.models.deletion.CASCADE, to='Klienten.KlientenBus'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='datum',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='bus1', chained_model_field='team', on_delete=django.db.models.deletion.CASCADE, to='Einsatztage.Fahrtag'),
        ),
    ]