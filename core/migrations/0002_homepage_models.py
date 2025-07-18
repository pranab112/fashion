# Generated migration for homepage management models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomepageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('section_type', models.CharField(choices=[('hero_banner', 'Hero Banner'), ('deal_of_day', 'Deal of the Day'), ('exclusive_brands', 'Exclusive Brands'), ('top_picks', 'Top Picks'), ('shop_by_category', 'Shop by Category'), ('brand_deals', 'Brand Deals'), ('trending_now', 'Trending Now'), ('indian_wear', 'Indian Wear'), ('sports_wear', 'Sports Wear'), ('footwear', 'Footwear'), ('new_brands', 'New Brands')], max_length=50, unique=True, verbose_name='Section Type')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Homepage Section',
                'verbose_name_plural': 'Homepage Sections',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='HeroBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('subtitle', models.CharField(blank=True, max_length=300, verbose_name='Subtitle')),
                ('image', models.ImageField(upload_to='hero_banners/', verbose_name='Image')),
                ('link_url', models.URLField(blank=True, verbose_name='Link URL')),
                ('link_text', models.CharField(blank=True, max_length=100, verbose_name='Link Text')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Hero Banner',
                'verbose_name_plural': 'Hero Banners',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='HomepageSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Fashion Store', max_length=100, verbose_name='Site Name')),
                ('site_description', models.TextField(blank=True, verbose_name='Site Description')),
                ('hero_auto_play', models.BooleanField(default=True, verbose_name='Hero Auto Play')),
                ('hero_slide_duration', models.PositiveIntegerField(default=4, verbose_name='Hero Slide Duration (seconds)')),
                ('products_per_section', models.PositiveIntegerField(default=8, help_text='Number of products to show in each section', verbose_name='Products per Section')),
                ('brands_per_section', models.PositiveIntegerField(default=6, help_text='Number of brands to show in each section', verbose_name='Brands per Section')),
                ('categories_per_section', models.PositiveIntegerField(default=8, help_text='Number of categories to show in Shop by Category', verbose_name='Categories per Section')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Homepage Settings',
                'verbose_name_plural': 'Homepage Settings',
            },
        ),
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
            },
        ),
        migrations.AddConstraint(
            model_name='featuredproduct',
            constraint=models.UniqueConstraint(fields=('product', 'section'), name='unique_product_section'),
        ),
        migrations.AddConstraint(
            model_name='featuredbrand',
            constraint=models.UniqueConstraint(fields=('brand', 'section'), name='unique_brand_section'),
        ),
    ]
