from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django import forms

from .models import User, Category, Auction_Listing, Bid, Comment


class CommentForm(forms.Form):
    comment = forms.CharField(label=None, widget=forms.Textarea(attrs={'placeholder':'Comment here...', 'rows': 5, 'cols': 40}))


class CreateListingForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Title'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows': 5, 'cols': 40}))
    starting_bid = forms.DecimalField(max_digits=8, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Starting bid'}))
    image_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control','placeholder':'Image URL'}))


def index(request):
    active_listings = Auction_Listing.objects.filter(is_Active=True)
    active_listings = active_listings.order_by('-id')
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "active_listings" : active_listings,
        "categories" : categories
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = request.POST["category"]

            category_data = Category.objects.get(pk=category)
            """
            bid = Bid(user=request.user, bid=float(starting_bid))
            bid.save()
            """
            new_listing = Auction_Listing(
                user=request.user,
                title=title,
                description=description,
                starting_bid=float(starting_bid),
                image_url=image_url,
                category=category_data
            )

            new_listing.save()

            return HttpResponseRedirect(reverse("index"))

        else:
            categories = Category.objects.all()
            return render(request, "auctions/create.html",{
                "categories": categories,
                "create_listing_form" : form
            })


    categories = Category.objects.all()
    return render(request, "auctions/create.html",{
        "categories": categories,
        "create_listing_form" : CreateListingForm()
    })



def listing(request, listing_id):
    item = Auction_Listing.objects.get(id=listing_id)
    allComments = Comment.objects.filter(listing=listing_id)
    max_bid = Bid.objects.filter(listing_id=listing_id).aggregate(Max('amount'))['amount__max']
    bid_count = item.bids.count()
    # To get max bid make by a specific user
    bids = Bid.objects.filter(user=request.user, listing=item)

    if bids.exists():
        user_max_bid = bids.order_by('-amount').first().amount
    else:
        user_max_bid = None

    if max_bid is not None:
        max_bid = round(max_bid, 2)
    return render(request, "auctions/listing.html", {
        "item": item,
        "isWatchlisted": request.user in item.watchlist.all(),
        "comments": allComments,
        "max_bid": max_bid,
        "comment_form": CommentForm(),
        "user_max_bid": user_max_bid,
        "bid_count": bid_count
    })



def category(request):
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categories" : categories
    })



def category_items(request):
    if request.method == "POST":
        category_user = request.POST["category"]
        category = Category.objects.get(pk=category_user)
        auction_listings = Auction_Listing.objects.filter(category=category).all()
        return render(request, "auctions/categoryitems.html", {
            "auction_listings": auction_listings
        })



def watchlist(request):
    current_user = request.user
    watchlisted_items = current_user.user.all()
    return render(request, "auctions/watchlist.html", {
        "watchlisted_items" : watchlisted_items
    })



def remove_watchlist(request, listing_id):
    if request.method == "POST":
        listing_data = Auction_Listing.objects.get(pk=listing_id)
        listing_data.watchlist.remove(request.user)
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



def add_watchlist(request, listing_id):
    if request.method == "POST":
        listing_data = Auction_Listing.objects.get(pk=listing_id)
        listing_data.watchlist.add(request.user)
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



def comment(request, listing_id):
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data["comment"]
            listing = Auction_Listing.objects.get(pk=listing_id)
            newComment = Comment(user=request.user, listing=listing, comment=comment)

            newComment.save()

        return HttpResponseRedirect(reverse("listing", args=(listing_id, )))



def bid(request, listing_id):
    if request.method == "POST":
        amount = float(request.POST["bid"])
        listing = Auction_Listing.objects.get(pk=listing_id)
        max_bid = Bid.objects.filter(listing_id=listing_id).aggregate(Max('amount'))['amount__max']

        if max_bid == None:
            max_bid = 0.0

        if amount > listing.starting_bid and amount > max_bid:
            newBid = Bid(user=request.user, listing=listing, amount=amount)
            newBid.save()

            messages.success(request, 'Your bid was added successfully.')
        else:
            messages.error(request, 'Sorry!! Your bid was not added.')

        return HttpResponseRedirect(reverse("listing", args=(listing_id, )))



def close_auction(request, listing_id):
    if request.method == "POST":
        listing = Auction_Listing.objects.get(pk=listing_id)

        # Get highest bid for this listing
        highest_bid = listing.bids.order_by('-amount').first()

        # Get highest bidding user
        highest_bid_user = highest_bid.user

        listing.winner = highest_bid_user
        listing.is_Active = False

        listing.save()

        messages.success(request, 'Auction closed successfully!')

        return HttpResponseRedirect(reverse("listing", args=(listing_id, )))



def my_bids(request):
    bids = Bid.objects.filter(user=request.user)
    listings = Auction_Listing.objects.filter(bids__in=bids).distinct()

    return render(request, "auctions/mybids.html", {
        "listings": listings
    })



def my_listings(request):
    listings = Auction_Listing.objects.filter(user=request.user)

    return render(request, "auctions/mylistings.html", {
        "listings": listings
    })