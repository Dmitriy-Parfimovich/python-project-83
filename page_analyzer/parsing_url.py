#!/usr/bin/env python


from bs4 import BeautifulSoup
import requests


def parsing_url(name):
    resp = requests.get(name)
    soup = BeautifulSoup(resp.text, 'html.parser')
    if soup.h1:
        url_h1 = soup.h1.string
    else:
        url_h1 = ''
    if soup.title:
        url_title = soup.title.string
    else:
        url_title = ''
    if soup.find('meta', {'name': 'description'}):
        url_description = soup.find(
            'meta', {'name': 'description'}).get('content')
    else:
        url_description = ''
    return url_h1, url_title, url_description
