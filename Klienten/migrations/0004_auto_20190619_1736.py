# Generated by Django 2.2.2 on 2019-06-19 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Klienten', '0003_auto_20190619_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='klienten',
            name='bemerkung',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
