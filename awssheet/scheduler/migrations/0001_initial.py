# Generated by Django 4.2.8 on 2024-02-29 11:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('command', models.TextField()),
                ('schedule', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TaskResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.TextField()),
                ('execution_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='scheduler.scheduledtask')),
            ],
        ),
    ]
