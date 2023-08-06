#!/usr/bin/env python3


def find_index(input):
    index = -1
    for char in str(input):
        if char.isdigit():
            index = int(char)
    index -= 1
    return index
