# Generated by Django 2.2.3 on 2019-07-09 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Einsatzmittel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fahrer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('mobil', models.CharField(max_length=30)),
                ('aktiv', models.BooleanField(default=True, max_length=1)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Einsatzmittel.Bus')),
            ],
            options={
                'verbose_name': 'Fahrer',
                'verbose_name_plural': 'Fahrer',
            },
        ),
        migrations.CreateModel(
            name='Buerokraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('mobil', models.CharField(max_length=30)),
                ('aktiv', models.BooleanField(default=True, max_length=1)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Einsatzmittel.Buero')),
            ],
            options={
                'verbose_name': 'Bürokraft',
                'verbose_name_plural': 'Bürokräfte',
            },
        ),
    ]
