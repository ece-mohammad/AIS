from django.contrib.auth.models import User, UserManager
from django.urls import reverse_lazy

# Create your models here.


class MemberManager(UserManager):
    def active(self):
        """Return active members"""
        return self.filter(is_active=True)

    def inactive(self):
        """Return inactive members"""
        return self.filter(is_active=False)


class Member(User):
    """Site member model"""

    objects = MemberManager()

    class Meta(User.Meta):
        proxy = True

    def get_absolute_url(self):
        return reverse_lazy("accounts:profile", kwargs={"user_name": self.username})
