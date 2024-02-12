# Generated by Django 5.0 on 2024-01-01 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_alter_ticket_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airline',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='passenger',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='airline',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ticket.airline'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='passenger',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ticket.passenger'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='sector',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='travel_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]