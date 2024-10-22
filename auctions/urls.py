from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("myListings/", views.my_listings, name="mylistings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categoryitems", views.category_items, name="categoryitems"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("removeWatchlist/<int:listing_id>", views.remove_watchlist, name="removeWatchlist"),
    path("addWatchlist/<int:listing_id>", views.add_watchlist, name="addWatchlist"),
    path("addComment/<int:listing_id>", views.comment, name="addComment"),
    path("addBid/<int:listing_id>", views.bid, name="addBid"),
    path("closeAuction/<int:listing_id>", views.close_auction, name="closeAuction"),
    path("myBids/", views.my_bids, name="myBids")
]
