from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category_name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category_name}"


class Auction_Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=400)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_Active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="user")
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="won_listings")

    def __str__(self):
        return f"{self.id}: {self.user}, Title: {self.title}, Starting Bid: {self.starting_bid}, Category: {self.category}"


class Bid(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="bid_user")
    listing = models.ForeignKey(Auction_Listing, null=True, blank=True, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} bid {self.amount} on listing: {self.listing}"


class Comment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    listing = models.ForeignKey(Auction_Listing, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.CharField(max_length=400)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} commented on Listing: {self.listing}"
