# Generated by Django 5.2 on 2025-05-15 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_remove_posthistory_last_edited_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='last_edited_by',
            field=models.CharField(default='API', max_length=50),
        ),
        migrations.AlterField(
            model_name='posthistory',
            name='editor',
            field=models.CharField(max_length=50),
        ),
    ]
