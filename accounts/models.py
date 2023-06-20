from django.contrib.auth.models import User
from django.urls import reverse_lazy

# Create your models here.


class Member(User):
    """Site member model"""
    
    class Meta(User.Meta):
        proxy = True
    
