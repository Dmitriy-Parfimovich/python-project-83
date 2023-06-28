#!/usr/bin/env python


from bs4 import BeautifulSoup
import requests


def parsing_url(name):
    resp = requests.get(name)
    soup = BeautifulSoup(resp.text, 'html.parser')
    url_h1 = soup.h1.string if soup.h1 else ''
    url_title = soup.title.string if soup.title else ''
    url_description = soup.find('meta', {'name': 'description'}).get('content') if soup.find('meta', {'name': 'description'}) else '' # noqa
    return url_h1, url_title, url_description
