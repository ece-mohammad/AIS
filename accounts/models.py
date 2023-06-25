from django.contrib.auth.models import User
from django.urls import reverse_lazy

# Create your models here.


class Member(User):
    """Site member model"""
    
    class Meta(User.Meta):
        proxy = True
    
    def get_absolute_url(self):
        return reverse_lazy("accounts:profile", kwargs={"user_name": self.username})
    
    def active_members(self):
        """Return active members"""
        return self.objects.filter(is_active=True)

    def inactive_members(self):
        """Return inactive members"""
        return self.objects.filter(is_active=False)
