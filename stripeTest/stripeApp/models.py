from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

CURRENCY_CHOICES = (
    ('BYN', 'BYN'),
    ('USD', 'USD'),
)
DURATION_CHOICES = (
    ('once', 'once'),
    ('repeating', 'repeating'),
    ('forever', 'forever'),
)


class Item(models.Model):
    name = models.TextField(max_length=100, unique=True)
    description = models.TextField()
    price = models.IntegerField()
    img = models.ImageField(upload_to='images/', default='images/default.png')
    currency = models.CharField(max_length=6, choices=CURRENCY_CHOICES, default='BYN')

    def __str__(self):
        return f"{self.name}"


class Discount(models.Model):
    name = models.CharField(max_length=50)
    percent_off = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=50)
    inclusive = models.BooleanField(default=False)
    percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.name


class Order(models.Model):
    order_items = models.ManyToManyField(Item, blank=True)
    currency = models.CharField(max_length=6, choices=CURRENCY_CHOICES, default='BYN')
    discounts = models.ManyToManyField(Discount, blank=True)
    tax = models.ManyToManyField(Tax, blank=True)

    def __str__(self):
        return f'Заказ № {self.pk}'
