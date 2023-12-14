from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("uploadItem", views.uploadItem, name="uploadItem"),
    path("categoryView", views.categoryView, name="categoryView"),
    path("itemListing/<int:item_id>", views.itemListing, name="itemListing"),
    path("watchList", views.watchList, name="watchList"),
    path("addWatchList/<int:item_id>", views.addWatchList, name="addWatchList"),
    path("deleteWatchList/<int:item_id>", views.deleteWatchList, name="deleteWatchList"),
    path("biding/<int:item_id>", views.biding, name="biding"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("closeBid/<int:item_id>", views.closeBid, name="closeBid"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)