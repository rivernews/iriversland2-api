# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-13 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20190117_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casestudy',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(blank=True),
        ),
    ]
