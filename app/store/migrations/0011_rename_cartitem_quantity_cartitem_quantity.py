# Generated by Django 4.2.7 on 2024-04-11 05:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_rename_quantity_cartitem_cartitem_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='cartItem_quantity',
            new_name='quantity',
        ),
    ]
