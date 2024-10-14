from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name


class AuctionListing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    current_bid = models.DecimalField(max_digits=10, decimal_places=2) 
    photo = models.ImageField(upload_to='listings/', null=True, blank=True)
    datetime_submitted = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} added {self.listing} in your watchlist."

    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    datetime_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} submitted a bid of {self.value} on the {self.listing} listing."


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    content = models.TextField()
    datetime_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} commented {self.content} on the {self.listing} listing."
