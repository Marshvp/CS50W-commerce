from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib import messages


from .models import User, Listing, Bid, Comment, Watchlist

#######
def index(request):
    active_listing = Listing.objects.filter(status='active')
    

    return render(request, "auctions/index.html", {'active_listing': active_listing})

#######
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

#######
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

#######
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
    
#######
@login_required
def create_page(request):
    
    if request.method == "POST":
        print("POST RECIEVED")
        
        title = request.POST['Title']
        desc = request.POST['Desc']
        startP = request.POST['Starting']
        imgURL = request.POST['ImgURL']
        cat = request.POST['Category']
        
        validate = URLValidator()
        try:
            validate(imgURL)
        except ValidationError:
            imgURL = None
        
        print(title, desc, startP, imgURL, cat)
        
        new_listing = Listing(
            title=title,
            description=desc,
            image_url=imgURL,
            category=cat,
            starting_price=startP,
            current_price=startP,
            seller=request.user
        )
        
        new_listing.save()
        return redirect('index')
    
    print("Hello create")
    
    return render(request, "auctions/create.html")



#######
def listing_page (request, listing_id):

    listing = get_object_or_404(Listing, pk=listing_id)
    bids = Bid.objects.filter(listing=listing).order_by('-date_placed')
    is_watchlisted = False
    comments = listing.comments.all()


    if request.user.is_authenticated:
        watchlisted_ids = Watchlist.objects.filter(user=request.user).values_list('listing_id', flat=True)
        is_watchlisted = listing.id in watchlisted_ids
    

    context = {
        'listing': listing,
        'is_watchlisted': is_watchlisted,
        'bids': bids,
        'comments': comments
    }
    if listing.status == 'closed':
        return render(request, "auctions/closedlisting.html",context)
    return render(request, "auctions/listingpage.html",context)


######
@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.method == "POST" and listing.status == Listing.ACTIVE:
        bid_amount = request.POST.get("bid_amount")

        try:
            bid_amount = float(bid_amount)
        except (TypeError, ValueError):
            messages.error(request, "Invalid bid amount.")
            return redirect('listing_page', listing_id=listing_id)
        
        if bid_amount > listing.current_price:
            Bid.objects.create(
                bidder=request.user,
                bid_amount=bid_amount,
                listing=listing
            )

            listing.current_price = bid_amount
            listing.save()
            print("item saved")
        else:
            print("must be higher. Will do error tommorrow")
    print("Updted Price: ", listing.current_price)
    return redirect('listing_page', listing_id=listing_id)


######

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlisted_item, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)

    if created:
        # Item was successfully added to the watchlist
        pass  # You can add any additional logic here if needed
        print("Item added to Watchlist")
    else:
        watchlisted_item.delete()
        print("Item removed from Watchlist")
    return redirect('listing_page', listing_id=listing_id)

######
@login_required
def watchlist_page(request):
    users_watchlist = Watchlist.objects.filter(user=request.user)

    watchlisted_items = []

    for item in users_watchlist:
        watchlisted_items.append(item.listing)



    return render(request, "auctions/watchlist.html", {'watchlisted' : watchlisted_items})


######
def category_page(request, category_name=None):

    categories = Listing.objects.filter(status='active').values_list('category', flat=True).distinct()

    if category_name:
        listings = Listing.objects.filter(category=category_name, status='active')
    else:
        listings = Listing.objects.filter(status='active')
    

    return render(request, 'auctions/category.html', {'categories': categories, 'listings': listings, 'selected_category': category_name })

    #####
@login_required
def addcomment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        comment_text = request.POST.get('comment_text', '').strip()

        if comment_text:
            Comment.objects.create(
                listing=listing,
                user=request.user,
                text=comment_text,
                date_posted=timezone.now()
            )
            messages.success(request, 'Your comment has been posted.')
        else:
            messages.error(request, 'Comment text cannot be empty.')

    return redirect('listing_page', listing_id=listing_id)



######
@login_required
def closeauction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.user != listing.seller:
        messages.error(request, "You are not the seller so this is not authorised")
        return redirect('listingpage', listing_id=listing_id)

    if request.method == "GET": 
        if listing.status == Listing.ACTIVE:
            highest_bid = Bid.objects.filter(listing=listing).order_by('-bid_amount').first()
            if highest_bid:

                listing.winner = highest_bid.bidder
                listing.current_price = highest_bid.bid_amount
            else:
                messages.error(request, "There were no bids placed")
            
            listing.status = listing.CLOSED
            listing.save()
            print("Item closed")
            messages.success(request, "Closed Listing")
    print("not closed")
    return redirect('listing_page', listing_id=listing_id)