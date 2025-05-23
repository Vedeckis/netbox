# Generated by Django 5.2b1 on 2025-04-04 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0126_exporttemplate_file_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='configtemplate',
            name='as_attachment',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='configtemplate',
            name='file_extension',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='configtemplate',
            name='file_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='configtemplate',
            name='mime_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='environment_params',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
