# Generated migration for adding vendor fields to CustomUser

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('customer', 'Customer'), ('vendor', 'Vendor'), ('admin', 'Admin')], default='customer', max_length=20, verbose_name='User type'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_vendor_approved',
            field=models.BooleanField(default=False, help_text='Designates whether this vendor has been approved to sell products.', verbose_name='Vendor approved'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='vendor_commission_rate',
            field=models.DecimalField(decimal_places=2, default=10.0, help_text='Commission percentage charged on vendor sales', max_digits=5, verbose_name='Vendor commission rate'),
        ),
    ]
