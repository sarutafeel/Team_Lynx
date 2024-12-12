# Generated by Django 4.2.16 on 2024-12-05 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0008_remove_student_major'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='completed_courses',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='tutorials.student'),
        ),
    ]