from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Category)
admin.site.register(models.AuctionListing)
admin.site.register(models.Watchlist)
admin.site.register(models.Comment)
admin.site.register(models.Bid)