# Generated by Django 5.1.6 on 2025-04-08 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_transaction_status_alter_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='billing_address',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_address',
            field=models.JSONField(),
        ),
    ]
