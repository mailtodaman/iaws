# Generated by Django 4.2.8 on 2024-03-10 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_logsmodel_delete_chatgptmodel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logsmodel',
            old_name='log_type',
            new_name='log_name',
        ),
    ]
