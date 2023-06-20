""" 
Test title parser, that title parser can parse title from a webpage

Test cases:
    - title parser can parse title from a webpage with title tag
    - title parser doesn't parse title from a webpage without title tag
    - title parser can parse title from a webpage with multiple title tags
    - title parser can parse title from google

"""
import pytest
from typing import *
from urllib import request

from tests.utils.title_parser import TitleParser


PAGE_WITH_TITLE: Final[str] = """<html><head><title>Test title</title></head><body></body></html>"""
PAGE_WITH_NO_TITLE: Final[str] = """<html><head></head><body></body></html>"""
PAGE_WITH_MULTIPLE_TITLES: Final[str] = """<html><head><title>Test title</title><title>Test title 2</title></head><body></body></html>"""


@pytest.fixture(scope="module", autouse=True)
def title_parser() -> TitleParser:
    tp = TitleParser()
    yield tp
    tp.close()


# title parser can parse title from a webpage with title tag
def test_title_parser_gets_title_from_page_with_title(title_parser: TitleParser):
    title_parser.feed(PAGE_WITH_TITLE)
    assert title_parser.get_title() == "Test title"


# title parser doesn't parse title from a webpage without title tag
def test_title_parser_does_not_get_title_from_page_with_no_title(title_parser: TitleParser):
    title_parser.feed(PAGE_WITH_NO_TITLE)
    assert title_parser.get_title() == None


# title parser can parse title from a webpage with multiple title tags
def test_title_parser_gets_title_from_page_with_multiple_title_tags(title_parser: TitleParser):
    title_parser.feed(PAGE_WITH_MULTIPLE_TITLES)
    assert title_parser.get_title() == "Test title"


def test_title_parser_gets_title_from_google(title_parser: TitleParser):
    req = request.Request("https://www.google.com")
    rsp = request.urlopen(req)
    title_parser.feed(rsp.read().decode("utf-8"))
    assert title_parser.get_title() == "Google"
