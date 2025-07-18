# Generated migration for creating vendor models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_add_vendor_fields'),
        ('users', '0002_add_vendor_fields'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payout_frequency', models.CharField(choices=[('weekly', 'Weekly'), ('biweekly', 'Bi-weekly'), ('monthly', 'Monthly')], default='monthly', max_length=20, verbose_name='Payout frequency')),
                ('bank_account_name', models.CharField(blank=True, max_length=200, verbose_name='Bank account name')),
                ('bank_account_number', models.CharField(blank=True, max_length=50, verbose_name='Bank account number')),
                ('bank_name', models.CharField(blank=True, max_length=100, verbose_name='Bank name')),
                ('bank_routing_number', models.CharField(blank=True, max_length=50, verbose_name='Bank routing number')),
                ('total_sales', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Total sales')),
                ('total_orders', models.PositiveIntegerField(default=0, verbose_name='Total orders')),
                ('average_rating', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=3, verbose_name='Average rating')),
                ('total_reviews', models.PositiveIntegerField(default=0, verbose_name='Total reviews')),
                ('id_document', models.FileField(blank=True, null=True, upload_to='vendor_documents/id/', verbose_name='ID document')),
                ('business_license', models.FileField(blank=True, null=True, upload_to='vendor_documents/license/', verbose_name='Business license')),
                ('tax_document', models.FileField(blank=True, null=True, upload_to='vendor_documents/tax/', verbose_name='Tax document')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to='users.customuser', verbose_name='User')),
            ],
            options={
                'verbose_name': 'Vendor profile',
                'verbose_name_plural': 'Vendor profiles',
            },
        ),
        migrations.CreateModel(
            name='VendorPayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20, verbose_name='Status')),
                ('period_start', models.DateField(verbose_name='Period start')),
                ('period_end', models.DateField(verbose_name='Period end')),
                ('transaction_id', models.CharField(blank=True, max_length=100, verbose_name='Transaction ID')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('processed_at', models.DateTimeField(blank=True, null=True, verbose_name='Processed at')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to='users.customuser', verbose_name='Vendor')),
            ],
            options={
                'verbose_name': 'Vendor payout',
                'verbose_name_plural': 'Vendor payouts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='VendorOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Subtotal')),
                ('commission_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Commission amount')),
                ('vendor_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Vendor amount')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_orders', to='cart.order')),
                ('payout', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='products.vendorpayout')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_orders', to='users.customuser', verbose_name='Vendor')),
            ],
            options={
                'verbose_name': 'Vendor order',
                'verbose_name_plural': 'Vendor orders',
                'unique_together': {('order', 'vendor')},
            },
        ),
    ]
