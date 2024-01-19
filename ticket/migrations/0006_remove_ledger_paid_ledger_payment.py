# Generated by Django 5.0 on 2024-01-02 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0005_customer_opening_balance_supplier_opening_balance_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ledger',
            name='paid',
        ),
        migrations.AddField(
            model_name='ledger',
            name='payment',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
