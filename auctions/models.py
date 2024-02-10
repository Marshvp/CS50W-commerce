from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):

    # Model fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=255, null=True)


    seller = models.ForeignKey(User, related_name='listings', on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name='won_listings', null=True, blank=True, on_delete=models.SET_NULL)
    
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status choices
    ACTIVE = 'active'
    CLOSED = 'closed'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return self.title



class Bid(models.Model):
    # Model fields
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(Listing, related_name='bids', on_delete=models.CASCADE)
    date_placed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.bid_amount}"
    

class Comment(models.Model):
    listing = models.ForeignKey(Listing, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.title}"

    class Meta:
        ordering = ['-date_posted']


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watched_by")

    class Meta:
        unique_together = ('user', 'listing')  

    def __str__(self):
        return f"{self.user.username} is watching {self.listing.title}"
