# Generated by Django 5.1.3 on 2024-11-29 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutorials", "0002_user_role_lessonrequest_lessonschedule"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("tutor", "Tutor"),
                    ("admin", "Admin"),
                ],
                default="student",
                max_length=10,
            ),
        ),
    ]