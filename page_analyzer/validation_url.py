#!/usr/bin/env python


from urllib.parse import urlparse
import validators


def validation_url(new_url):
    messages = []
    incorrect_url_err = ('error', 'Некорректный URL')
    length_of_url_err = ('error', 'URL превышает 255 символов')
    url_required = ('error', 'URL обязателен')
    work_url = urlparse(new_url)
    if work_url.scheme:
        new_url = f'{work_url.scheme}://{work_url.netloc}'.lower()
    elif not work_url.scheme and len(work_url) > 255:
        messages.append(incorrect_url_err)
        messages.append(length_of_url_err)
    valid_new_url_flag = validators.url(new_url)
    if len(new_url) > 255:
        messages.append(length_of_url_err)
        if not valid_new_url_flag:
            messages.append(incorrect_url_err)
    elif not valid_new_url_flag:
        messages.append(incorrect_url_err)
        if not new_url:
            messages.append(url_required)
    return new_url, messages
