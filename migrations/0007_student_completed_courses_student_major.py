# Generated by Django 4.2.16 on 2024-12-05 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0006_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='completed_courses',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='student',
            name='major',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
