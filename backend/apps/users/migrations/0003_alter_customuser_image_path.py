# Generated by Django 5.1.2 on 2024-11-07 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='image_path',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
