# Generated migration for adding vendor fields to Brand model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('users', '0002_add_vendor_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='vendor',
            field=models.ForeignKey(blank=True, help_text='The vendor who owns this brand', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brands', to='users.customuser', verbose_name='Vendor'),
        ),
        migrations.AddField(
            model_name='brand',
            name='is_verified',
            field=models.BooleanField(default=False, help_text='Designates whether this brand has been verified by admin', verbose_name='Verified'),
        ),
        migrations.AddField(
            model_name='brand',
            name='commission_rate',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Custom commission rate for this brand (overrides vendor default)', max_digits=5, null=True, verbose_name='Commission rate'),
        ),
        migrations.AddField(
            model_name='brand',
            name='shop_banner',
            field=models.ImageField(blank=True, null=True, upload_to='brands/banners/', verbose_name='Shop banner'),
        ),
        migrations.AddField(
            model_name='brand',
            name='shop_description',
            field=models.TextField(blank=True, help_text='Detailed description for the brand shop page', verbose_name='Shop description'),
        ),
        migrations.AddField(
            model_name='brand',
            name='return_policy',
            field=models.TextField(blank=True, help_text='Brand-specific return policy', verbose_name='Return policy'),
        ),
        migrations.AddField(
            model_name='brand',
            name='shipping_info',
            field=models.TextField(blank=True, help_text='Brand-specific shipping information', verbose_name='Shipping information'),
        ),
        migrations.AddField(
            model_name='brand',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Contact email'),
        ),
        migrations.AddField(
            model_name='brand',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Contact phone'),
        ),
        migrations.AddField(
            model_name='brand',
            name='business_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Business name'),
        ),
        migrations.AddField(
            model_name='brand',
            name='tax_id',
            field=models.CharField(blank=True, max_length=50, verbose_name='Tax ID'),
        ),
    ]
