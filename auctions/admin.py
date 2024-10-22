from django.contrib import admin

from .models import User, Category, Auction_Listing, Comment, Bid

# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction_Listing)
admin.site.register(Comment)
admin.site.register(Bid)