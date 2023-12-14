from django.contrib import admin

from auctions.models import Bid, Comment, Item, User, WatchList

# Register your models here.
admin.site.register(User)
admin.site.register(Item)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(WatchList)