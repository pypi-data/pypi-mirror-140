#!/usr/bin/env python3

from os import stat
from os.path import abspath, exists, join
from dvk_archive.test.temp_dir import get_test_dir
from dvk_archive.main.web.bs_connect import bs_connect
from dvk_archive.main.web.bs_connect import basic_connect
from dvk_archive.main.web.bs_connect import download
from dvk_archive.main.web.bs_connect import get_default_headers
from dvk_archive.main.web.bs_connect import get_direct_response
from dvk_archive.main.web.bs_connect import get_last_modified
from dvk_archive.main.web.bs_connect import json_connect

def test_get_direct_response():
    """
    Tests the get_direct_response function.
    """
    # Test getting response headers
    url = "http://pythonscraping.com/exercises/exercise1.html"
    response = get_direct_response(url, get_default_headers())
    headers = response.headers
    assert headers["Server"] == "nginx"
    assert headers["Connection"] == "keep-alive"
    # Test getting response using invalid parameters
    assert get_direct_response() is None
    assert get_direct_response(None) is None
    assert get_direct_response("") is None
    assert get_direct_response("asdfghjkl") is None

def test_basic_connect():
    """
    Tests the basic_connect function
    """
    # Test getting HTML page
    url = "http://pythonscraping.com/exercises/exercise1.html"
    html = basic_connect(url)
    assert html is not None
    assert html.startswith("<html>\n<head>\n<title>A Useful Page</title>")
    # Test getting invalid HTML page
    assert basic_connect() is None
    assert basic_connect(None) is None
    assert basic_connect("") is None
    assert basic_connect("asdfghjkl") is None

def test_bs_connect():
    """
    Tests the bs_connect function.
    """
    # Test getting BeautifulSoup object from page
    url = "http://pythonscraping.com/exercises/exercise1.html"
    bs = bs_connect(url)
    assert bs is not None
    assert bs.find("h1").get_text() == "An Interesting Title"
    assert bs.find("title").get_text() == "A Useful Page"
    # Test getting invalid page
    assert bs_connect() is None
    assert bs_connect(None) is None
    assert bs_connect("") is None
    assert bs_connect("qwertyuiop") is None

def test_json_connect():
    """
    Tests the json_connect function.
    """
    # Test loading page as a JSON object
    json = json_connect("https://jsonplaceholder.typicode.com/users/3/posts")
    assert len(json) == 10
    element = json[0]
    assert element["userId"] == 3
    assert element["id"] == 21
    assert element["title"] == "asperiores ea ipsam voluptatibus modi minima quia sint"
    # Test loading an invalid page
    json = json_connect("asdfghjkl")
    assert json is None
    json = json_connect(None)
    assert json is None

def test_download():
    """
    Tests the download function.
    """
    # Test downloading a given file
    test_dir = get_test_dir()
    file = abspath(join(test_dir, "image.jpg"))
    url = "http://www.pythonscraping.com/img/gifts/img6.jpg"
    download(url, file)
    assert exists(file)
    assert stat(file).st_size == 39785
    # Test downloading with invalid parameters
    file = join(test_dir, "invalid.jpg")
    download(None, None)
    assert not exists(file)
    download(None, file)
    assert not exists(file)
    download("asdfasdf", file)
    assert not exists(file)
    download(url, None)
    assert not exists(file)

def test_get_last_modified():
    """
    Tests the get_last_modified function.
    """
    d = {"Last-Modified": "Udf, 10 Jan 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/01/10|12:05"
    d = {"Last-Modified": "Udf, 23 Feb 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/02/23|20:23"
    d = {"Last-Modified": "Udf, 01 Mar 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/03/01|12:00"
    d = {"Last-Modified": "Udf, 10 Apr 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/04/10|12:05"
    d = {"Last-Modified": "Udf, 23 May 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/05/23|20:23"
    d = {"Last-Modified": "Udf, 01 Jun 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/06/01|12:00"
    d = {"Last-Modified": "Udf, 10 Jul 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/07/10|12:05"
    d = {"Last-Modified": "Udf, 23 Aug 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/08/23|20:23"
    d = {"Last-Modified": "Udf, 01 Sep 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/09/01|12:00"
    d = {"Last-Modified": "Udf, 10 Oct 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/10/10|12:05"
    d = {"Last-Modified": "Udf, 23 Nov 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/11/23|20:23"
    d = {"Last-Modified": "Udf, 01 Dec 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/12/01|12:00"
    # Test invalid times
    d = {"Last-Modified": "Udf, 10 Nop 2010 12:05:55 GMT"}
    assert get_last_modified(d) == ""
    d = {"Last-Modified": "Mon, BB Aug FFFF GG:TT:PP GMT"}
    assert get_last_modified(d) == ""
    d = {"Last-Modified": ""}
    assert get_last_modified(d) == ""
    assert get_last_modified() == ""
    assert get_last_modified(dict()) == ""
    assert get_last_modified(None) == ""

def all_tests():
    """
    Runs all tests for the bs_connect module.
    """
    test_get_direct_response()
    test_basic_connect()
    test_bs_connect()
    test_json_connect()
    test_download()
    test_get_last_modified()
