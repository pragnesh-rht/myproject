# Generated by Django 2.1.4 on 2019-03-30 13:31

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('b2b', '0007_auto_20190330_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='date_end',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 1, 13, 31, 10, 704144, tzinfo=utc), verbose_name='End Date'),
        ),
    ]
