# Generated by Django 3.2.6 on 2023-08-22 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_authentication', '0006_userapproval_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='approval',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
