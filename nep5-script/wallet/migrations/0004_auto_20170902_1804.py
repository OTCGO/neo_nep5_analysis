# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-02 10:04
from __future__ import unicode_literals
from decimal import Decimal
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0003_auto_20170902_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('uid', models.CharField(max_length=10)),
                ('type', models.IntegerField(default=Decimal('0'), null=True)),
                ('name', models.CharField(max_length=64)),
                ('nickName', models.CharField(max_length=50)),
                ('bankName', models.CharField(max_length=50)),
                ('sort', models.PositiveSmallIntegerField(default=0)),
                ('accountWithBank', models.CharField(max_length=50)),
                ('account', models.CharField(max_length=50)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('createdTime', models.DateTimeField(auto_now_add=True)),
                ('modifiedTime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='bank',
            name='uid',
            field=models.CharField(max_length=10),
        ),
    ]
