# Generated by Django 5.1.2 on 2024-11-20 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_company_admins'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companyinvitation',
            unique_together=set(),
        ),
    ]
