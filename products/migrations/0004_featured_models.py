# Generated migration to add featured models to products app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_vendor_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(choices=[('deal_of_day', 'Deal of the Day'), ('top_picks', 'Top Picks'), ('trending_now', 'Trending Now'), ('indian_wear', 'Indian Wear'), ('sports_wear', 'Sports Wear'), ('footwear', 'Footwear')], max_length=50, verbose_name='Section')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('featured_until', models.DateTimeField(blank=True, help_text='Leave blank for permanent featuring', null=True, verbose_name='Featured Until')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_in', to='products.product')),
            ],
            options={
                'verbose_name': 'Featured Product',
                'verbose_name_plural': 'Featured Products',
                'ordering': ['section', 'order', 'created_at'],
                'unique_together': {('product', 'section')},
            },
        ),
        migrations.CreateModel(
            name='FeaturedCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Custom Title')),
                ('custom_image', models.ImageField(blank=True, help_text='Leave blank to use category image', null=True, upload_to='featured_categories/', verbose_name='Custom Image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_in', to='products.category')),
            ],
            options={
                'verbose_name': 'Featured Category',
                'verbose_name_plural': 'Featured Categories',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='FeaturedBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(choices=[('exclusive_brands', 'Exclusive Brands'), ('brand_deals', 'Brand Deals'), ('new_brands', 'New Brands')], max_length=50, verbose_name='Section')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Custom Title')),
                ('subtitle', models.CharField(blank=True, max_length=300, verbose_name='Subtitle')),
                ('discount_text', models.CharField(blank=True, max_length=100, verbose_name='Discount Text')),
                ('custom_image', models.ImageField(blank=True, help_text='Leave blank to use brand logo', null=True, upload_to='featured_brands/', verbose_name='Custom Image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('featured_until', models.DateTimeField(blank=True, help_text='Leave blank for permanent featuring', null=True, verbose_name='Featured Until')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_in', to='products.brand')),
            ],
            options={
                'verbose_name': 'Featured Brand',
                'verbose_name_plural': 'Featured Brands',
                'ordering': ['section', 'order', 'created_at'],
                'unique_together': {('brand', 'section')},
            },
        ),
    ]
