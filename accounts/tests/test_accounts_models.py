from typing import *

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse_lazy

from accounts.models import Member

ACTIVE_MEMBERS_DATA: Final[List[Dict[str, str]]] = [
    dict(
        username="active_user_1",
        first_name="Active",
        last_name="User 1",
        email="active_user1@domain.com",
        password="test_password_1",
    ),
    dict(
        username="active_user_2",
        first_name="Active",
        last_name="User 2",
        email="active_user2@domain.com",
        password="test_password_2",
    ),
    dict(
        username="active_user_3",
        first_name="Active",
        last_name="User 3",
        email="active_user3@domain.com",
        password="test_password_3",
    ),
]

INACTIVE_MEMBERS_DATA: Final[List[Dict[str, str]]] = [
    dict(
        username="inactive_user_1",
        first_name="Inactive",
        last_name="User 1",
        email="inactive_user1@domain.com",
        password="test_password_1",
        is_active=False,
    ),
    dict(
        username="inactive_user_2",
        first_name="Inactive",
        last_name="User 2",
        email="inactive_user2@domain.com",
        password="test_password_2",
        is_active=False,
    ),
    dict(
        username="inactive_user_3",
        first_name="Inactive",
        last_name="User 3",
        email="inactive_user3@domain.com",
        password="test_password_3",
        is_active=False,
    ),
]


class BaseMemberModelTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.members = Member.objects.bulk_create(
            [
                Member(**member_data)
                for member_data in ACTIVE_MEMBERS_DATA + INACTIVE_MEMBERS_DATA
            ],
            ignore_conflicts=True,
        )

        return super().setUp()


class TestMemberModel(BaseMemberModelTestCase):
    def test_member_is_user(self):
        """Test that Member is a subclass of User"""
        self.assertTrue(issubclass(Member, User))

    def test_member_active_members_manager(self):
        """Test that Member has an active_members manager"""
        active_members = Member.objects.active().order_by("username")

        for index, member in enumerate(active_members):
            member_data = ACTIVE_MEMBERS_DATA[index]
            self.assertEqual(member.username, member_data["username"])
            self.assertEqual(member.first_name, member_data["first_name"])
            self.assertEqual(member.last_name, member_data["last_name"])
            self.assertEqual(member.email, member_data["email"])
            self.assertEqual(member.password, member_data["password"])

    def test_member_inactive_members_manager(self):
        """Test that Member has an inactive_members manager"""
        inactive_members = Member.objects.inactive().order_by("username")

        for index, member in enumerate(inactive_members):
            member_data = INACTIVE_MEMBERS_DATA[index]
            self.assertEqual(member.username, member_data["username"])
            self.assertEqual(member.first_name, member_data["first_name"])
            self.assertEqual(member.last_name, member_data["last_name"])
            self.assertEqual(member.email, member_data["email"])
            self.assertEqual(member.password, member_data["password"])
            self.assertEqual(member.is_active, member_data["is_active"])

    def test_member_absolute_url(self):
        """Test that Member has an absolute url"""
        member = self.members[0]
        self.assertEqual(
            member.get_absolute_url(),
            reverse_lazy("accounts:profile", kwargs={"user_name": member.username}),
        )
