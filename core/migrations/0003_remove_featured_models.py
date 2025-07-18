# Generated migration to remove featured models from core app

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_homepage_models'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='featuredproduct',
            name='unique_product_section',
        ),
        migrations.RemoveConstraint(
            model_name='featuredbrand',
            name='unique_brand_section',
        ),
        migrations.DeleteModel(
            name='FeaturedProduct',
        ),
        migrations.DeleteModel(
            name='FeaturedBrand',
        ),
        migrations.DeleteModel(
            name='FeaturedCategory',
        ),
    ]
