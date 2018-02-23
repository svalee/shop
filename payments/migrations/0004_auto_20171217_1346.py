# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-17 13:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0003_remove_product_order'),
        ('payments', '0003_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(to='showcase.Product'),
        ),
    ]
