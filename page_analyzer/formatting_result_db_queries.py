#!/usr/bin/env python


def get_url_checks_list(result_DB_query):
    url_checks_list = sorted([{'id': item[0],
                               'url_name': item[1],
                               'created_at': item[2],
                               'checks_id': item[3],
                               'checks_status_code': item[4],
                               'checks_h1': item[5],
                               'checks_title': item[6],
                               'checks_description': item[7],
                               'checks_created_at': item[8]}
                              for item in result_DB_query],
                             key=lambda k: k['checks_id'],
                             reverse=True)
    for item in url_checks_list:
        new_url = item['url_name']
        created_at = item['created_at']
        break
    url_checks_list = replace_none(url_checks_list)
    return new_url, created_at, url_checks_list


def get_urls(list_of_urls):
    urls = sorted([{'id': item[0],
                    'name': item[1],
                    'created_at': item[2],
                    'status_code': item[3]}
                  for item in list_of_urls],
                  key=lambda k: k['id'], reverse=True)
    urls = replace_none(urls)
    return urls


def replace_none(list_of_dicts):
    for item in list_of_dicts:
        for key in item.keys():
            if item[key] is None:
                item[key] = ''
    return list_of_dicts
