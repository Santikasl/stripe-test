# Generated by Django 4.1.6 on 2023-02-14 06:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripeApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('inclusive', models.BooleanField(default=False)),
                ('percentage', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='tax',
            field=models.ManyToManyField(blank=True, to='stripeApp.tax'),
        ),
    ]
