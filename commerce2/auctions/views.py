from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import Bid, Comment, Item, User, WatchList

from .forms import ItemForm

def index(request):
    items = Item.objects.all().order_by("-date")
    return render(request, "auctions/index.html", {
        "items": items,
        "watchlist": get_watch_list(request),
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
            messages.success(request, "Login successfully.")
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logout successfully.")
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
        messages.success(request, "Register successfully.")
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def uploadItem(request):
    if request.method == "POST":
        item = ItemForm(request.POST, request.FILES)
        if item.is_valid():
            data = item.save(commit=False)
            data.user_id = request.user
            data.save()
            messages.success(request, "Upload successfully.")
            return HttpResponseRedirect(reverse('uploadItem'))
    return render(request, "auctions/upload.html", {
        "item": ItemForm(),
        "watchlist": get_watch_list(request),
    })

def itemListing(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
        bids = Bid.objects.filter(item_id=item_id).order_by('-price')
        comment = Comment.objects.filter(item_id=item_id).order_by('-time')
        add = True
        watch = []
        if request.user.is_authenticated:
            watch = WatchList.objects.all().filter(item_id=item_id).filter(user_id=request.user)
        if len(watch) == 0:
            add = True
        else:
            add = False
        return render(request, "auctions/item.html", {
            "item": item,
            "add": add,
            "bidUsers": bids,
            "comments": comment,
            "watchlist": get_watch_list(request),
        })
    except Item.DoesNotExist:
        raise Http404("Item does not exist.")
    
@login_required
def addWatchList(request, item_id):
    if request.method == "POST":
        item = Item.objects.get(pk=item_id)
        list = WatchList.objects.create(item_id=item, user_id=request.user)
        list.save()
        messages.success(request, "Added item to watchlist.")
        return HttpResponseRedirect(reverse('itemListing', args=(item_id,)))
    
@login_required
def deleteWatchList(request, item_id):
    if request.method == "POST":
        list = WatchList.objects.all().filter(user_id=request.user).filter(item_id=item_id)
        list.delete()
        messages.success(request, "Removed item from watchlist.")
        return HttpResponseRedirect(reverse('itemListing', args=(item_id,)))

@login_required
def watchList(request):
    itemsWatch = WatchList.objects.all().filter(user_id=request.user)
    items = []
    for item in itemsWatch:
        i = item.item_id
        items.append(i)
    return render(request, "auctions/watchList.html", {
        "items": items,
        "watchlist": get_watch_list(request),
    })
    
def categoryView(request):
    items = Item.objects.all()
    if len(items) == 0:
        watchlist = 0
    else:
        watchlist = get_watch_list(request)
    category = Item.get_free_category()
    current = "."
    if request.method == "POST":
        category_id = request.POST['category']
        if category_id != None:
            if category_id == current:
                items = Item.objects.all()
                current = "."
            else:
                items = Item.objects.filter(category=category_id)
                current = category_id
    return render(request, "auctions/category.html", {
        "items": items,
        "category": category,
        "current": current,
        "watchlist": watchlist,
    })

@login_required
def biding(request, item_id):
    item = Item.objects.get(pk=item_id)
    price = float(request.POST['price'])
    currPrice = float(Item.get_current_price(item))
    if price <= currPrice:
        messages.success(request, f"Bided price must higher than: %.2f" % price)
        return HttpResponseRedirect(reverse('itemListing', args=(item_id,)))
    else:
        bid = Bid.objects.create(item_id=item, user_id=request.user, price=price)
        bid.save()
    messages.success(request, f"Bided {item.name} with price: %.2f" % price)
    return HttpResponseRedirect(reverse('itemListing', args=(item_id,)))

@login_required
def closeBid(request, item_id):
    if request.method == "POST":    
        item = Item.objects.get(pk=item_id)
        item.bided = True
        item.save()
        messages.success(request, "You closed the item.")
    return HttpResponseRedirect(reverse('itemListing', args=(item_id,)))

@login_required
def get_watch_list(request):
    itemsWatch = WatchList.objects.all().filter(user_id=request.user)
    return itemsWatch

@login_required
def comment(request, item_id):
    item = Item.objects.get(pk=item_id)
    content = request.POST['content']
    comment = Comment.objects.create(item_id=item, user_id=request.user, content=content)
    comment.save()
    messages.success(request, "Comment added.")
    return HttpResponseRedirect(reverse('itemListing', args=(item_id,)))