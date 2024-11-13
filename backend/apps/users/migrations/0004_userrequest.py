# Generated by Django 5.1.2 on 2024-11-11 18:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_alter_companyinvitation_status'),
        ('users', '0003_alter_customuser_image_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected'), ('C', 'Canceled')], default='P', max_length=1)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='company.company')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'unique_together': {('company', 'sender')},
                'verbose_name_plural': 'User Requests'
            },
        ),
    ]
