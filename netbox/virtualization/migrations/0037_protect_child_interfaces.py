# Generated by Django 4.2.6 on 2023-10-20 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0023_squashed_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vminterface',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name='child_interfaces',
                to='virtualization.vminterface',
            ),
        ),
    ]
