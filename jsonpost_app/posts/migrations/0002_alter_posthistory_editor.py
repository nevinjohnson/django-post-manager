# Generated by Django 5.2 on 2025-05-15 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posthistory',
            name='editor',
            field=models.CharField(default='API', max_length=50),
        ),
    ]
