# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 12:14:13 2022

@author: aarid
scrape and clean web page into lists of text from <p> tags and list of words.

"""

from html.parser import HTMLParser
import urllib.request
import string

from anpa_tools import anpatools
 
#
def access_webpage(url):
    """
    Opens and reads a webpage from URL and returns raw HTML from webpage.
    """
    webpage = urllib.request.urlopen(url)
    content = webpage.read().decode()
    return content

class ParserHTML(HTMLParser):
    """Inherits from HTMLParser in python standard library.
    Parses text from inside <p> tags, adds text to a list, returns the list"""
    data_list = []
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_data = False
    def handle_starttag(self, tag, attrs): #why the attrs parameter?
        if tag == 'p':
            self.is_data = True
    def handle_endtag(self, tag):
        if tag == 'p':
            self.is_data = False
    def handle_data(self, data):
        if self.is_data:
            self.data_list.append(data)
        return self.data_list


def parse_page(content):
    """
    Takes raw html as input and parses text from <p> tags.
    Returns a list of parsed text
    """
    pars = ParserHTML()
    pars.feed(str(content))
    parsed_data = pars.data_list
    return parsed_data

def clean_data(data_list):
    """
    Takes a list of strings and iterates through the list to make all letters 
    lowercase and remove punctuation. Appends the cleaned strings to a new 
    list. Returns the new list.
    """
    string_list = []
    for item in data_list:
        item = item.lower()
        item = item.translate(str.maketrans('', '', string.punctuation))
        string_list.append(item)
    return string_list

def split_sentence(string_list):
    """
    Takes a list of sentences or multi-word strings and iterates through the 
    list to split each sentence into a list of words. Iterates through the 
    words, and appends each word once to a new list. Returns new list.
    """
    word_list = []
    for items in string_list:
        words = items.split(' ')
        for word in words:
            word = word.replace('\n', '')
            word = word.replace('\\', '')
            if word != '' and word not in word_list:
                word_list.append(word)
    return word_list