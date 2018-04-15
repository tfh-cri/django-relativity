from __future__ import absolute_import, unicode_literals

from django.db import models
from django.db.models import Q, Lookup
from django.db.models.fields import Field
from django.utils.encoding import python_2_unicode_compatible

from relationships.fields import L, Relationship


@Field.register_lookup
class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params


@python_2_unicode_compatible
class Page(models.Model):
    slug = models.TextField()
    descendants = Relationship(
        'self', Q(slug__startswith=L('slug'), slug__ne=L('slug')),
        related_name='ascendants'
    )

    def __str__(self):
        return self.slug


@python_2_unicode_compatible
class Categorised(models.Model):
    category_codes = models.TextField()


@python_2_unicode_compatible
class Category(models.Model):
    code = models.TextField(unique=True)
    members = Relationship(
        Categorised,
        Q(category_codes__contains=L('code')),
        related_name='categories',
    )

    def __str__(self):
        return "Category #%d: %s" % (self.pk, self.code)


@python_2_unicode_compatible
class Product(models.Model):
    sku = models.CharField(max_length=13)
    colour = models.CharField(max_length=20)
    shape = models.CharField(max_length=20)
    size = models.IntegerField()

    def __str__(self):
        return "Product #%s: a %s %s, size %s" % (self.sku, self.colour, self.shape, self.size)


@python_2_unicode_compatible
class CartItem(models.Model):
    product_code = models.CharField(max_length=13)
    description = models.TextField()

    product = Relationship(
        Product,
        Q(sku=L('product_code')),
        related_name='cart_items',
        multiple=False,
    )

    def __str__(self):
        return "Cart item #%s: SKU %s" % (self.pk, self.sku)


@python_2_unicode_compatible
class ProductFilter(models.Model):
    fcolour = models.CharField(max_length=20)
    fsize = models.IntegerField()

    products = Relationship(
        Product,
        Q(colour=L('fcolour'), size__gte=L('fsize')),
        related_name='filters',
    )
