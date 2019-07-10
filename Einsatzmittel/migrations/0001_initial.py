# Generated by Django 2.2.3 on 2019-07-09 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Buero',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buero', models.CharField(max_length=20)),
                ('buerotage', models.CharField(choices=[(None, 'Bitte Bürotage auswählen'), ('Mo,Di,Mi,Do', 'Montag, Dienstag, Mittwoch und Donnerstag')], default='Mo,Di,Mi,Do', max_length=20)),
                ('wird_verwaltet', models.BooleanField(default=False, max_length=1)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Büro',
                'verbose_name_plural': 'Büros',
            },
        ),
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('bus', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('fahrtage', models.CharField(choices=[(None, 'Bitte Bus-Fahrtage auswählen'), ('Di,Do', 'Dienstag und Donnerstag'), ('Mi,Fr', 'Mittwoch und Freitag')], default='Di,Do', max_length=20)),
                ('wird_verwaltet', models.BooleanField(default=False, max_length=1)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Bus',
                'verbose_name_plural': 'Busse',
            },
        ),
    ]