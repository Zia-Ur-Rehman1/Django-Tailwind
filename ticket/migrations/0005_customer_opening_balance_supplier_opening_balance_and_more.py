# Generated by Django 5.0 on 2024-01-01 14:04

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0004_alter_airline_name_alter_passenger_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='opening_balance',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='opening_balance',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Ledger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid', models.PositiveIntegerField(blank=True, null=True)),
                ('payment_date', models.DateField(default=django.utils.timezone.now)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ticket.customer')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ticket.supplier')),
            ],
        ),
    ]
