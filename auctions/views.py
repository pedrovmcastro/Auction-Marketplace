from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, AuctionListing, Category, Watchlist, Comment, Bid
from . import forms


def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.all()
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


def categories(request):
    return render(request, 'auctions/categories.html', {
        'categories': Category.objects.all()
    })


def category_matches(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = AuctionListing.objects.filter(category=category)

    return render(request, 'auctions/category_matches.html', {
        'category': category,
        'listings': listings
    })


def listing_details(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    # Watchlist logic
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
        bid_form = forms.CreateBidForm()
        comment_form = forms.CreateCommentForm()
    else:
        in_watchlist = False
        bid_form = None
        comment_form = None

    # Bids logic
    bids = Bid.objects.filter(listing=listing)
    highest_bid = bids.aggregate(Max('value'))['value__max']
    current_highest_bid = None
    if highest_bid:
        current_highest_bid = bids.get(value=highest_bid)

    # Comments logic
    comments = Comment.objects.filter(listing=listing)

    return render(request, 'auctions/listing_details.html', {
        'listing': listing,
        'in_watchlist': in_watchlist,
        'comments': comments,
        'bids': bids,
        'current_highest_bid': current_highest_bid,
        'comment_form': comment_form,
        'bid_form': bid_form
    })


@login_required
def create(request):
    if request.method == "POST":
        form = forms.CreateListingForm(request.POST, request.FILES)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.listed_by = request.user
            listing.save()
            return redirect('listing_details', listing.id)
    else:
        form = forms.CreateListingForm()

    return render(request, 'auctions/create.html', {
        'form': form
    })


@login_required
def watchlist(request):
    listings = AuctionListing.objects.filter(watchlist__user=request.user)
    return render(request, 'auctions/watchlist.html', {
        'watchlist': listings
    })


@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    watchlist_item = Watchlist.objects.filter(user=request.user, listing=listing).first()

    if watchlist_item:
        watchlist_item.delete()
    else:
        Watchlist.objects.create(user=request.user, listing=listing)
    
    return redirect('listing_details', listing_id)


@login_required
def bid(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    if request.method == "POST":
        bid_form = forms.CreateBidForm(request.POST)

        if bid_form.is_valid():
            bid_value = bid_form.cleaned_data['value']

            if bid_value > listing.current_bid:
                bid = bid_form.save(commit=False)
                bid.user = request.user
                bid.listing = listing
                bid.save()
                
                # Update listing current_bid
                listing.current_bid = bid.value 
                listing.save()

                return redirect('listing_details', listing_id)
            else:
                messages.error(request, "Your bid must be higher than the current bid.")
                return redirect('listing_details', listing_id)
    else:
        bid_form = forms.CreateBidForm()

    return render(request, 'auctions/listing_details.html', {
        'listing': listing,
        'bid_form': bid_form,
    })


@login_required
def comment(request, listing_id):
    if request.method == "POST":
        comment_form = forms.CreateCommentForm(request.POST)

        if comment_form.is_valid():
            listing = get_object_or_404(AuctionListing, id=listing_id)
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.save()
            return redirect('listing_details', listing_id)
    else:
        comment_form = forms.CreateCommentForm()
    
    return render(request, 'auctions/listing_details.html', {
        'comment_form': comment_form
    })
    