# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 05:48:02 2022

@author: aarid
"""

import itertools
from collections import Counter, defaultdict


class StringObject:
    """Various functions for stored strings"""
    def __init__(self, string):
        self.string = string
        self.sub_string = None
        self.loaded_string = None
        self.save_file = None


    def __repr__(self):
        """Return a string representation of string object"""
        return self.string

    def substring(self, substring):
        """set value of self.sub_string"""
        self.sub_string = substring
        return self.sub_string

    def append(self):
        """
        Appends a sub_string to string, and returns the appended string.

        >>> test = StringObject()
        >>> test.string = 'This is my string'
        >>> print(test.string)
        This is my string
        >>> test.sub_string = ', but only for now.'
        >>> print(test.append(test.sub_string))
        This is my string, but only for now.
        """
        appended = str(self.string) + str(self.sub_string)
        return appended

    def remove(self):
        """
        Removes a sub_string from string, and returns the truncated string.

        >>> test = StringObject()
        >>> test.string = 'This is my string, but only for now.'
        >>> print(test.string)
        This is my string, but only for now.
        >>> test.sub_string = ', but only for now.'
        >>> print(test.remove(test.sub_string))
        This is my string
        >>> test.sub_string = 'This is my string,'
        >>> print(test.remove(test.sub_string))
        but only for now.
        """
        truncated = self.string.replace(str(self.sub_string), '')
        return truncated

    def mirror_string(self):
        """
        Returns the mirrored string of string.

        >>> test = StringObject()
        >>> test.string = 'This is my string'
        >>> print(test.string)
        This is my string
        >>> print(test.mirror_string())
        gnirts ym si sihT
        """
        mirror = str(self.string[::-1])
        return mirror

    def load_string(self, load_file):
        """Loads a string from load_file and returns that string."""
        with open(load_file) as load_string:
            self.loaded_string = load_string.read()
        return self.loaded_string

    def save_string(self, save_file):
        """Saves the string to save_file."""
        with open(save_file, 'w') as saved:
            saved.write(self.string)


class Anagram(StringObject):
    """Inherits from StringObject class and can get anagrams of string."""
    def __init__(self):
        super().__init__(self)
        self.string = None
        self.words = []

    def find_anagrams(self, words):
        """Takes a list of words, and hashes the letter frequency of each word
        as keys in a dictionary and creates a value list to which words having
        the same letter frequency are appended to the list. Returns the values
        if the length of the list is greater than 1.
        """
        anagrams_dict = defaultdict(list)
        self.words = words
        for word in words:
            if len(word) > 2:
                anagrams_dict[frozenset(dict(Counter(word)).items())].append(word)
        return [anagrams for key, anagrams in anagrams_dict.items() if len(anagrams) > 1]


    def create_all_anagrams(self):
        """Takes string and returns a list of string's anagrams (permutations)."""
        anagrams = [''.join(perm) for perm in itertools.permutations(self.string)]
        return anagrams


class Palyndrome(StringObject):
    """Inherits from StringObject and can identify palindromes."""
    def __init__(self, string):
        super().__init__(self)
        self.string = string

    def find_palindromes(self):
        """Checks if mirrored string is equal to string.
        If true, returns the mirrored string."""
        mirror = StringObject.mirror_string(self)
        if mirror == str(self.string) and len(mirror) > 2:
            palindrome = mirror
            return palindrome
