#!/usr/bin/env/ python3

from dvk_archive.main.processing.list_processing import clean_list
from dvk_archive.main.processing.list_processing import list_to_string

def test_clean_list():
    """
    Tests the clean_list function.
    """
    # SET UP LIST
    lst = ["these"]
    lst.append("are")
    lst.append("things")
    lst.append("")
    lst.append(None)
    lst.append("are")
    # TEST CLEANING ARRAY
    lst = clean_list(lst)
    assert len(lst) == 4
    assert lst[0] == "these"
    assert lst[1] == "are"
    assert lst[2] == "things"
    assert lst[3] == ""
    # TEST CLEANING INVALID ARRAY
    lst = clean_list(None)
    assert len(lst) == 0

def test_list_to_string():
    """
    Tests the list_to_string function.
    """
    # Test getting strings with no indent
    string = list_to_string(["List", "of", "items!"])
    assert string == "List,of,items!"
    # Test getting string with indent
    string = list_to_string(["things", "stuff!"], indent=1)
    assert string == "things, stuff!"
    string = list_to_string(["some", "more", "Things."], indent=4)
    assert string == "some,    more,    Things."
    # Test getting string with invalid indent value
    string = list_to_string(["False", "Indent"], indent=-1)
    assert string == "False,Indent"
    string = list_to_string(["other", "indent", "value"], indent=-29)
    assert string == "other,indent,value"
    # Test adding escape characters to items
    string = list_to_string(["item!", ",,", "Other Item"], True)
    assert string == "item&#33;,&#44;&#44;,Other Item"
    string = list_to_string(["Don't", "forget", "Escapes!"], True, 1)
    assert string == "Don&#39;t, forget, Escapes&#33;"
    # Test getting string with invalid list
    assert list_to_string([]) == ""
    assert list_to_string(None) == ""

def all_tests():
    """
    Runs all tests for the list_processing module:
    """
    test_clean_list()
    test_list_to_string()
