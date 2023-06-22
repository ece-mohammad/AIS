""" 
Provides helper functions for testing

Functions:
----------

    - get_page_template(page: Page) -> Template
    - page_title_in_response(page: Page, response: HttpResponse) -> bool
    - is_same_url(page: Page, response: HttpResponse) -> bool
    - is_redirection_target(page: Page, response: HttpResponse) -> bool
    - page_in_response(page: Page, response: HttpResponse) -> Tuple[bool, Dict[str, bool]]
    - client_login(client: Client, credentials: Dict[str, str]) -> bool
    - client_logout(client: Client) -> HttpResponse
    - member_signup(client, user_data: Dict[str, str], follow=False) -> HttpResponse
    - response_user_logged_in(response: HttpResponse) -> bool
    - create_member(username: str, password: str, first_name: str = None, last_name: str|None = None, email: str|None = None):
    
"""

from typing import *

from django.http import HttpResponse
from django.template import Template
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.test.client import Client

from accounts.models import Member
from tests.pages.common import LogIn, Page, SignUp
from tests.utils.title_parser import TitleParser


def get_page_template(page: Page) -> Template:
        """
        Get template object from page's template name
        
        :param page: Page instance to get template from
        :param type: Page
        :return: Template object
        :rtype: Template instance
        :raises: TemplateDoesNotExist if template name is not recognized by 
        Django's template loader
        """
        return get_template(page.template_name).template


def page_title_in_response(page: Page, response: HttpResponse) -> bool:
    """
    Check if given response instance's title is same as page's title
    
    :param page: Page instance to check it's title against given response
    :param type: Page
    :param response: HttpResponse instance to check for title
    :param type: HttpResponse
    :return: True if page's title is in response, False otherwise
    :rtype: bool
    :raises: ValueError if response's charset is not recognized
    """
    title_parser = TitleParser()
    title_parser.feed(
        response.content.decode(
            response.charset if response.charset else "utf-8"
        )
    )
    
    return page.title == title_parser.get_title().strip()


def is_same_url(page: Page, response: HttpResponse) -> bool:
    """
    Check if page's url is same as response's url
    
    :param page: Page instance to check it's url against given response
    :param type: Page
    :param response: HttpResponse instance to check for url
    :param type: HttpResponse
    :return: True if page's url is same as response's url, False otherwise
    :rtype: bool
    :raises: AttributeError if response instance doesn't have url attribute
    """
    return page.url == response.url


def is_redirection_target(page: Page, response: HttpResponse) -> bool:
    """
    Check if the page is the last target of the response's redirection chain

    :param page: Page instance to check if it's the target of the response's
    :param type: Page
    :param response: HttpResponse instance to check for redirection target
    :param type: HttpResponse
    :return: True if page is the target of the response's redirection chain,
    :rtype: bool
    :raises: AttributeError if response instance doesn't have redirect_chain
    attribute
    """
    return response.redirect_chain[-1] == (page.url, 302)


def page_in_response(page: Page, response: HttpResponse) -> Tuple[bool, Dict[str, bool]]:
    """
    Check if page is in response by checking for page's title, template and
    view name in response
    
    :param page: Page instance to check if it's in response
    :param type: Page
    :param response: HttpResponse instance to check for page
    :param type: HttpResponse
    :return: A tuple of bool and dict of bools. Tuple's first element is True
    if response's title, template and view name are same as the page's, false
    otherwise. Tuple's second element is a dict of bools with keys as test
    names and values as True if test passed, False otherwise.
    :rtype: Tuple[bool, Dict[str, bool]]
    :raises: ValueError if response's charset is not recognized
    :raises: TemplateDoesNotExist if template name is not recognized by
    """
    tests = dict(
        has_title = page_title_in_response(page, response),
        using_template = get_page_template(page) in response.templates,
        current_view = page.view_name == response.resolver_match.view_name,
    )
    
    return all(tests.values()), tests


def client_login(client: Client, credentials: Dict[str, str]) -> HttpResponse:
        """ 
        Logs in the client, and returns True if the login was successful, False otherwise. 
        
        :param client: The client to use for the request
        :type client: Client
        :param credentials: The credentials to use for the login
        :type credentials: Dict[str, str], optional
        :return: The response from the login view
        :rtype: HttpResponse
        """
        return client.post(
            LogIn.url,
            data=credentials,
            follow=True
        )
    
    
def client_logout(client: Client, follow=False) -> HttpResponse:
    """ 
    Logs out the client, and returns the response from the logout view
    
    :param client: The client to use for the request
    :type client: Client
    :param follow: Whether to follow redirects or not
    :type follow: bool
    :return: The response from the logout view
    :rtype: HttpResponse
    """
    return client.post(reverse_lazy("accounts:logout"), follow=follow)


def member_signup(client: Client, user_data: Dict[str, str], follow=False) -> HttpResponse:
    """ 
    Signs up a new user with given user_data, and returns the response from the signup view. 
    
    :param client: The client to use for the request
    :type client: Client
    :param user_data: The data to use for the new user
    :type user_data: Dict[str, str]
    :param follow: Whether to follow redirects or not
    :type follow: bool
    :return: The response from the signup view
    :rtype: HttpResponse
    """
    client.get(SignUp.url)
    return client.post(SignUp.url, data=user_data, follow=follow,)


def response_user_logged_in(response: HttpResponse) -> bool:
    """ 
    Checks that response is from a logged in user
    
    :param response: The response to check
    :type response: HttpResponse
    :return: True if the response is from a logged in user, False otherwise
    :rtype: bool
    """
    if response.context is None:
        return False
    
    user = response.context.get("user", None)
    
    if user is None:
        return False
    
    return user.is_authenticated


def create_member(username: str, password: str, first_name: str = "", last_name: str = "", email: str = ""):
    """ 
    Create a new member with given username and password, and returns the new member.
    
    :param username: The username to use for the new member, must be a non empty string
    :type username: str
    :param password: The password to use for the new member, must be a non-empty string
    :type password: str
    :param first_name: The first name to use for the new member, defaults to empty string
    :type first_name: str, optional
    :param last_name: The last name to use for the new member, defaults to empty string
    :type last_name: str, optional
    :param email: The email to use for the new member, defaults to empty string
    :type email: str, optional
    :return: The new member
    :rtype: Member
    :raises: IntegrityError if username is not unique
    :raises: Integrity if username or password is empty
    :raises: TypeError if username or password is not a string
    """
    
    member = Member(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    member.set_password(password)
    member.save()
    return member

