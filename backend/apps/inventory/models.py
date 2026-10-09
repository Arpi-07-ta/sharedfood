from django.db import models


class InventoryItem(models.Model):
    """Placeholder inventory record for stock tracking and expiry monitoring."""

    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.FloatField(default=0)
    unit = models.CharField(max_length=50, default='kg')
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
