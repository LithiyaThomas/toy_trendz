# Generated by Django 3.2.25 on 2024-07-04 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_productvariant_is_active'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]