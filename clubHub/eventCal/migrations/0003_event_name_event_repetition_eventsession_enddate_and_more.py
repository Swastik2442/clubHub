# Generated by Django 4.2.7 on 2023-11-18 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cHub', '0005_alter_clubmember_role'),
        ('eventCal', '0002_subevent_location_eventoperationsteam_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(default='nd', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='repetition',
            field=models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly'), ('YEARLY', 'Yearly'), ('NULL', 'Null')], default='NULL', max_length=7),
        ),
        migrations.AddField(
            model_name='eventsession',
            name='endDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='eventsession',
            name='startDate',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subevent',
            name='endDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subevent',
            name='startDate',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='endDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizingHead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='cHub.student'),
        ),
    ]