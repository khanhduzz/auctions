from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORIES_CHOICE = [
    ("EL", "Electronic"),
    ("FN", "Furniture"),
    ("VE", "Vehicle"),
    ("TO", "Tool"),
    ("FO", "Food"),
    ("CL", "Cloth"),
    ("EQ", "Equipment"),
    ("", "None"),
]

class User(AbstractUser):
    pass

class Item(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=2,
        choices= CATEGORIES_CHOICE,
        default=""
    )
    first_price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="auctions/static/images", null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name="itemsListed")
    bided = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id}: {self.name}"
    
    @property
    def get_image_url(self):
        if not self.image:
            return ""
        return self.image.url
    
    @property
    def get_category(self):
        return CATEGORIES_CHOICE
    
    def get_free_category():
        return CATEGORIES_CHOICE
    
    def get_current_price(self):
        bid = self.itemBids.all().order_by('-price')
        if len(bid) > 0:
            return bid[0].price
        return self.first_price
    
class Bid(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="itemBids")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userBids")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_id.last_name} bided {self.price} on {self.item_id.name}"
    
    @property
    def get_max_price(self):
        bids = Bid.objects.filter(item_id=self.id).order_by("-price")
        if not bids:
            return self.first_price
        return bids[0].price
    
    def get_current_price(self):
        bid = self.itemBids.all().order_by('-price')
        if len(bid) > 0:
            return bid[0].price
        return self.first_price

class Comment(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="itemComts")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userComts")
    content = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_id.last_name} commented on {self.item_id.name}"
    
class WatchList(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="itemWatch")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userWatch")
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_id.last_name} add {self.item_id.name} to watchlist."
