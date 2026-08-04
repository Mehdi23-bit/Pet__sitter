from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser): 
    """  
        User Model : main model used to in login ,
        inherite from the Model AbstractUser ,
        we used email as username.
        
    """  
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('sitter', 'Sitter'),
    ]  
    email  = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True,null=True,defaut='avatars/default.png')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='owner')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','role']

    def __str__(self):
        return f"User({self.email},{self.role})" 



class SitterProfile(models.Model):
    """ 
   SitterProfile Model : model responsible for the sitters ,
   it has a relationship of OneToOne with User Model.
   
    """
    user                     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sitter')
    bio                      = models.TextField(blank=True)
    price_per_day            = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    accepts_dogs             = models.BooleanField(default=True)
    accepts_cats             = models.BooleanField(default=True)
    accepts_other            = models.BooleanField(default=False)
    rating                   = models.FloatField(default=0.0)
    is_premium               = models.BooleanField(default=False)
    latitude                 = models.FloatField(null=True, blank=True)
    longitude                = models.FloatField(null=True, blank=True)
    review_count             = models.PositiveIntegerField(default=0) 
    completed_bookings_count = models.PositiveIntegerField(default=0)
    city                     = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Sitter: {self.user.email}"


class SitterPhoto(models.Model):
    """ 
    SitterPhoto Model : model responsible on the photos uploaded by the
    sitters ,it hold the ForeignKey of Sitters responsible on.
    """
    sitter    = models.ForeignKey(SitterProfile,on_delete=models.CASCADE)
    photo     = models.ImageField(upload_to='sitters/',blank=False,null=False)
    upload_at = models.DateTimeField(auto_now_add=True)
