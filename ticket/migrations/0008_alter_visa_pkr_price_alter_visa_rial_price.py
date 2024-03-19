# Generated by Django 5.0.1 on 2024-03-18 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0007_visa_created_at_alter_visa_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visa',
            name='pkr_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='visa',
            name='rial_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
