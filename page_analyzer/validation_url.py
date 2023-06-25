#!/usr/bin/env python


from flask import (
    flash,
    get_flashed_messages
)
from urllib.parse import urlparse
import validators


def validation_url(new_url):
    work_url = urlparse(new_url)
    if work_url.scheme:
        new_url = f'{work_url.scheme}://{work_url.netloc}'.lower()
    elif not work_url.scheme and len(work_url) > 255:
        flash('Некорректный URL', 'error')
        flash('URL превышает 255 символов', 'error')
    valid_new_url_flag = validators.url(new_url)
    if len(new_url) > 255:
        flash('URL превышает 255 символов', 'error')
        if not valid_new_url_flag:
            flash('Некорректный URL', 'error')
    elif not valid_new_url_flag:
        flash('Некорректный URL', 'error')
    messages = get_flashed_messages(with_categories=True)
    return messages
