# Generated by Django 5.1.6 on 2025-03-20 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_category_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='SubCategory',
            new_name='subcategory',
        ),
    ]
