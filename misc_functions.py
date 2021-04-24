"""
This file contains functions the bot needs but that are not part of the bot_client class.
This makes everything more organized.
"""
import random
from typing import List


def startswithElement(string: str, lst: list) -> bool:
    # This function returns 'True' if str starts with at least one element
    # of list. Else it returns 'False'
    for el in lst:
        if string.startswith(el):
            return True

    # This line is only reached if no element is found
    return False


def unique_shuffle_list(originalList: list, maxStep: int = 10000):
    randomizedList = originalList[:]
    step: int = 0
    while True:
        random.shuffle(randomizedList)
        step += 1
        if not has_el_on_same_index(randomizedList, originalList) or step >= maxStep:
            return randomizedList


def has_el_on_same_index(l1: list, l2: list) -> bool:
    for i in range(min(len(l1), len(l2))):
        if l1[i] == l2[i]:
            return True
    return False


def int_in_str(string: str) -> int:
    dig: str = ''
    for char in string:
        if char.isdigit():
            dig += char
    return int(dig)


def bool_to_int(state: bool) -> int:
    if state:
        return 1
    else:
        return 0


def int_to_bool(num: int) -> bool:
    if num == 0:
        return False
    else:
        return True


def element_in_str(lst: List, s: str) -> bool:
    for el in lst:
        if el in s:
            return True
    return False
