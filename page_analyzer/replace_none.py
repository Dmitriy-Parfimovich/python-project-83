#!/usr/bin/env python


def replace_None(list_of_dicts):
    for item in list_of_dicts:
        for key in item.keys():
            if item[key] is None:
                item[key] = ''
    return list_of_dicts
