# Generated by Django 5.1.3 on 2024-12-13 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutorials", "0002_alter_studentrequest_preferred_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tutorrequest",
            name="available_time",
            field=models.TimeField(blank=True, null=True),
        ),
    ]
