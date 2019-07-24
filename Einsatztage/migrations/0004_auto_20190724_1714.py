# Generated by Django 2.2.3 on 2019-07-24 15:14

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('Einsatztage', '0003_auto_20190713_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fahrtag',
            name='fahrer_vormittag',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='team', chained_model_field='team', null=True, on_delete=django.db.models.deletion.CASCADE, to='Team.Fahrer'),
        ),
    ]
