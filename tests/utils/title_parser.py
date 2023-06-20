""" 
A custom HTML parser for getting the title of a page from its HTML content
"""

from html.parser import HTMLParser
from typing import *


class TitleParser(HTMLParser):
    """ 
    A custom HTML parser for getting the title of a page
    
    :attr is_title_tag: A boolean to check if current tag is title tag
    :type is_title_tag: bool
    :attr title: A string to hold the title of the page. If parser doesn't
    encounter title tag, it will be None
    :type title: str
    
    :usage:
    >>> parser = TitleParser()
    >>> parser.feed("<html><head><title>Page Title</title></head></html>")
    ... "Page Title"
    >>> parser.get_title()
    ... "Page Title"
    
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capture_data: bool = False
        self.title: str = None
    
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """
        Check if given tag is title tag and set is_title_tag to True,
        otherwise set it to False

        :param tag: Tag to check if it's title tag
        :param type: str
        :param attrs: List of tuples of attributes and their values
        :param type: list[tuple[str, str | None]]
        :return: None
        :rtype: None
        """
        if self.title is None and tag == "title":
            self.capture_data = True
    
    def handle_endtag(self, tag: str) -> str|None:
        """
        Check if given tag is title tag and set is_title_tag to False,
        and return current title 
        
        """
        if tag == "title":
            self.capture_data = False
    
    def handle_data(self, data: str) -> None:
        """ 
        get the data of the title tag
        """
        if self.capture_data:
            if self.title:
                self.title += data
            else:
                self.title = data
    
    def get_title(self) -> str | None:
        """ 
        get the title of the last encountered title tag
        
        :return: title of the last encountered title tag, or None
        if no title tag was encountered
        :rtype: str | None
        """
        return self.title