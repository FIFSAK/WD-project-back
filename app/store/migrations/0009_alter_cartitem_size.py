# Generated by Django 4.2.7 on 2024-04-11 05:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_cartitem_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cartItem_size', to='store.size'),
        ),
    ]