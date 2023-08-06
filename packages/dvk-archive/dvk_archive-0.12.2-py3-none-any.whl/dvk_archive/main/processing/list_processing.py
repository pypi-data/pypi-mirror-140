#!/usr/bin/env python3

from dvk_archive.main.processing.html_processing import add_escapes
from typing import List

def clean_list(lst:List[str]=None) -> List[str]:
    """
    Removes all duplicate and null entries from a String array.

    :param lst: Given string list
    :type lst: list[str], optional
    :return: List without duplicate or None entries
    :rtype: list[str]
    """
    # RETURN AN EMPTY LIST IF GIVEN LIST IS NONE
    if lst is None:
        return []
    # REMOVE NONE ENTRIES
    out = lst
    i = 0
    while i < len(out):
        if out[i] is None:
            del out[i]
            i = i - 1
        # INCREMENT COUNTER
        i = i + 1
    # REMOVE DUPLICATE ENTRIES
    i = 0
    while i < len(out):
        k = i + 1
        while k < len(out):
            if out[i] == out[k]:
                del out[k]
                k = k - 1
            # INCREMENT K COUNTER
            k = k + 1
        # INCREMENT I COUNTER
        i = i + 1
    return out

def list_to_string(lst:List[str]=None,
                use_escapes:bool=False,
                indent:int=0) -> str:
    """
    Converts list[str] into a string with items separated by commas.

    :param lst: List[str] to convert to string, defaults to None
    :type lst: list[str], optional
    :param use_escapes: Whether to add HTML escape chars to items, defaults to None
    :type use_escapes: bool, optional
    :param indent: Number of spaces to add after separating commas, defaults to 0
    :type indent: int, optional
    :return: String with original items separated by commas
    :rtype: str
    """
    try:
        my_list = []
        my_list.extend(lst)
        # Add HTML escape characters if specified
        if use_escapes:
            for i in range(0, len(my_list)):
                my_list[i] = add_escapes(my_list[i])
        # Convert list into string
        string = ""
        for i in range(0, len(my_list)):
            # Add comma if necessary
            if i > 0:
                string = string + ","
                # Add indent
                for k in range(0, indent):
                    string = string + " "
            # Add string from list
            string = string + my_list[i]
        # Return string
        return string
    except:
        return ""
    
