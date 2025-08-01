# Generated by Django 5.2.3 on 2025-07-18 22:50

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0005_remove_vendorpayout_vendor_remove_vendorprofile_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('returned', 'Returned'), ('refunded', 'Refunded')], max_length=50, unique=True, verbose_name='Status Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
            ],
            options={
                'verbose_name': 'Order Status',
                'verbose_name_plural': 'Order Statuses',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50, unique=True, verbose_name='Order Number')),
                ('order_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Order ID')),
                ('customer_email', models.EmailField(max_length=254, verbose_name='Customer Email')),
                ('customer_phone', models.CharField(blank=True, max_length=20, verbose_name='Customer Phone')),
                ('shipping_first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('shipping_last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('shipping_address_line1', models.CharField(max_length=255, verbose_name='Address Line 1')),
                ('shipping_address_line2', models.CharField(blank=True, max_length=255, verbose_name='Address Line 2')),
                ('shipping_city', models.CharField(max_length=100, verbose_name='City')),
                ('shipping_state', models.CharField(max_length=100, verbose_name='State')),
                ('shipping_postal_code', models.CharField(max_length=20, verbose_name='Postal Code')),
                ('shipping_country', models.CharField(default='India', max_length=100, verbose_name='Country')),
                ('billing_first_name', models.CharField(max_length=100, verbose_name='Billing First Name')),
                ('billing_last_name', models.CharField(max_length=100, verbose_name='Billing Last Name')),
                ('billing_address_line1', models.CharField(max_length=255, verbose_name='Billing Address Line 1')),
                ('billing_address_line2', models.CharField(blank=True, max_length=255, verbose_name='Billing Address Line 2')),
                ('billing_city', models.CharField(max_length=100, verbose_name='Billing City')),
                ('billing_state', models.CharField(max_length=100, verbose_name='Billing State')),
                ('billing_postal_code', models.CharField(max_length=20, verbose_name='Billing Postal Code')),
                ('billing_country', models.CharField(default='India', max_length=100, verbose_name='Billing Country')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Subtotal')),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Tax Amount')),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Shipping Cost')),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Discount Amount')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total Amount')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('returned', 'Returned'), ('refunded', 'Refunded')], default='pending', max_length=20, verbose_name='Order Status')),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20, verbose_name='Payment Status')),
                ('payment_method', models.CharField(blank=True, max_length=50, verbose_name='Payment Method')),
                ('payment_gateway', models.CharField(blank=True, max_length=50, verbose_name='Payment Gateway')),
                ('payment_gateway_order_id', models.CharField(blank=True, max_length=100, verbose_name='Gateway Order ID')),
                ('customer_notes', models.TextField(blank=True, verbose_name='Customer Notes')),
                ('admin_notes', models.TextField(blank=True, verbose_name='Admin Notes')),
                ('tracking_number', models.CharField(blank=True, max_length=100, verbose_name='Tracking Number')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('shipped_at', models.DateTimeField(blank=True, null=True, verbose_name='Shipped at')),
                ('delivered_at', models.DateTimeField(blank=True, null=True, verbose_name='Delivered at')),
                ('is_multi_vendor', models.BooleanField(default=False, verbose_name='Multi-vendor Order')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_orders', to=settings.AUTH_USER_MODEL, verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200, verbose_name='Product Name')),
                ('product_sku', models.CharField(blank=True, max_length=100, verbose_name='Product SKU')),
                ('brand_name', models.CharField(blank=True, max_length=100, verbose_name='Brand Name')),
                ('size', models.CharField(blank=True, max_length=50, verbose_name='Size')),
                ('color', models.CharField(blank=True, max_length=50, verbose_name='Color')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Unit Price')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total Price')),
                ('vendor_commission_rate', models.DecimalField(decimal_places=2, default=10.0, max_digits=5, verbose_name='Commission Rate')),
                ('vendor_commission', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Vendor Commission')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('returned', 'Returned'), ('refunded', 'Refunded')], default='pending', max_length=20, verbose_name='Item Status')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sales.order', verbose_name='Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_order_items', to='products.product', verbose_name='Product')),
                ('product_variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_order_items', to='products.productvariant', verbose_name='Product Variant')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sold_items', to=settings.AUTH_USER_MODEL, verbose_name='Vendor')),
            ],
            options={
                'verbose_name': 'Order Item',
                'verbose_name_plural': 'Order Items',
            },
        ),
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Gross Amount')),
                ('commission_rate', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Commission Rate (%)')),
                ('commission_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Commission Amount')),
                ('platform_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Platform Fee')),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Net Amount')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='pending', max_length=20, verbose_name='Status')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='Approved at')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='Paid at')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commissions', to=settings.AUTH_USER_MODEL, verbose_name='Vendor')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commissions', to='sales.order', verbose_name='Order')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commissions', to='sales.orderitem', verbose_name='Order Item')),
            ],
            options={
                'verbose_name': 'Commission',
                'verbose_name_plural': 'Commissions',
                'ordering': ['-created_at'],
                'unique_together': {('vendor', 'order_item')},
            },
        ),
        migrations.CreateModel(
            name='OrderStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_status', models.CharField(blank=True, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('returned', 'Returned'), ('refunded', 'Refunded')], max_length=20, verbose_name='From Status')),
                ('to_status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('returned', 'Returned'), ('refunded', 'Refunded')], max_length=20, verbose_name='To Status')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Changed at')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_status_changes', to=settings.AUTH_USER_MODEL, verbose_name='Changed By')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='sales.order', verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Order Status History',
                'verbose_name_plural': 'Order Status Histories',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Payment ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('currency', models.CharField(default='INR', max_length=10, verbose_name='Currency')),
                ('payment_method', models.CharField(choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('upi', 'UPI'), ('net_banking', 'Net Banking'), ('wallet', 'Digital Wallet'), ('cod', 'Cash on Delivery'), ('bank_transfer', 'Bank Transfer')], max_length=20, verbose_name='Payment Method')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded'), ('partially_refunded', 'Partially Refunded')], default='pending', max_length=20, verbose_name='Payment Status')),
                ('gateway', models.CharField(blank=True, max_length=50, verbose_name='Payment Gateway')),
                ('gateway_transaction_id', models.CharField(blank=True, max_length=100, verbose_name='Gateway Transaction ID')),
                ('gateway_response', models.JSONField(blank=True, default=dict, verbose_name='Gateway Response')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('processed_at', models.DateTimeField(blank=True, null=True, verbose_name='Processed at')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='sales.order', verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payout_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Payout ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Payout Amount')),
                ('currency', models.CharField(default='INR', max_length=10, verbose_name='Currency')),
                ('bank_account_number', models.CharField(max_length=50, verbose_name='Bank Account Number')),
                ('bank_name', models.CharField(max_length=100, verbose_name='Bank Name')),
                ('ifsc_code', models.CharField(max_length=20, verbose_name='IFSC Code')),
                ('account_holder_name', models.CharField(max_length=100, verbose_name='Account Holder Name')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20, verbose_name='Status')),
                ('transaction_reference', models.CharField(blank=True, max_length=100, verbose_name='Transaction Reference')),
                ('processing_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Processing Fee')),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Net Amount Paid')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('processed_at', models.DateTimeField(blank=True, null=True, verbose_name='Processed at')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Completed at')),
                ('commissions', models.ManyToManyField(related_name='payouts', to='sales.commission', verbose_name='Commissions')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to=settings.AUTH_USER_MODEL, verbose_name='Vendor')),
            ],
            options={
                'verbose_name': 'Payout',
                'verbose_name_plural': 'Payouts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SalesReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=20, verbose_name='Report Type')),
                ('report_date', models.DateField(verbose_name='Report Date')),
                ('total_orders', models.PositiveIntegerField(default=0, verbose_name='Total Orders')),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Total Revenue')),
                ('total_items_sold', models.PositiveIntegerField(default=0, verbose_name='Total Items Sold')),
                ('total_commissions', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Total Commissions')),
                ('pending_orders', models.PositiveIntegerField(default=0, verbose_name='Pending Orders')),
                ('completed_orders', models.PositiveIntegerField(default=0, verbose_name='Completed Orders')),
                ('cancelled_orders', models.PositiveIntegerField(default=0, verbose_name='Cancelled Orders')),
                ('returned_orders', models.PositiveIntegerField(default=0, verbose_name='Returned Orders')),
                ('average_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Average Order Value')),
                ('total_refunds', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total Refunds')),
                ('net_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Net Revenue')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sales_reports', to=settings.AUTH_USER_MODEL, verbose_name='Vendor')),
            ],
            options={
                'verbose_name': 'Sales Report',
                'verbose_name_plural': 'Sales Reports',
                'ordering': ['-report_date'],
                'unique_together': {('report_type', 'report_date', 'vendor')},
            },
        ),
    ]
