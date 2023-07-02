#!/usr/bin/env python


import os
import requests
from flask import (
    Flask, flash, get_flashed_messages,
    url_for, render_template,
    request, redirect, abort
)
from page_analyzer.db_queries import (
    get_DB_select_name,
    get_DB_select_created_at,
    get_DB_select_id_exists,
    get_DB_select_id,
    get_DB_insert_url_checks,
    get_DB_insert_add_url,
    get_DB_url_page,
    get_DB_list_of_urls
)
from page_analyzer.formatting_result_db_queries import (
    get_url_checks_list,
    get_urls
)
from page_analyzer.parsing_url import parsing_url
from page_analyzer.validation_url import validation_url
from dotenv import load_dotenv
from datetime import date


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/urls/<id>')
def url_page(id):

    url_checks_list = []

    try:
        result_DB_query = get_DB_url_page(id)

    except Exception:
        abort(404)

    else:

        if isinstance(result_DB_query, list):
            new_url, created_at, url_checks_list = get_url_checks_list(result_DB_query) # noqa

        else:
            new_url, created_at = result_DB_query

        messages = get_flashed_messages(with_categories=True)

        return render_template('url_page.html', messages=messages, id=id,
                               new_url=new_url, created_at=created_at,
                               url_checks_list=url_checks_list)


@app.route('/urls/<id>/checks', methods=['POST'])
def url_checks(id):

    created_at = date.today()
    name = get_DB_select_name(id)

    try:
        resp = requests.get(name)

    except requests.exceptions.RequestException:
        created_at = get_DB_select_created_at(id)
        flash('Произошла ошибка при проверке', 'error')
        messages = get_flashed_messages(with_categories=True)

        return render_template('url_page.html', messages=messages, id=id,
                               new_url=name, created_at=created_at), 422

    else:
        url_status_code = resp.status_code
        if url_status_code == 200:
            url_h1, url_title, url_description = parsing_url(name)
            get_DB_insert_url_checks(id, url_status_code, url_h1,
                                     url_title, url_description,
                                     created_at)
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'error')

    return redirect(url_for('url_page', id=id), code=302)


@app.route('/urls')
def urls():

    urls = []
    list_of_urls = get_DB_list_of_urls()
    urls = get_urls(list_of_urls)

    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_url():
    created_at = date.today()
    new_url = request.form.get('url')

    new_url, messages = validation_url(new_url)

    if messages != []:
        return render_template('index.html', messages=messages,
                               new_url=new_url), 422

    if get_DB_select_id_exists(new_url):
        id = get_DB_select_id(new_url)
        flash('Страница уже существует', 'success')
        return redirect(url_for('url_page', id=id), code=302)

    get_DB_insert_add_url(new_url, created_at)
    id = get_DB_select_id(new_url)

    flash('Страница успешно добавлена', 'success')

    return redirect(url_for('url_page', id=id), code=302)


@app.errorhandler(404)
def page_not_found(err):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(err):
    return render_template('500.html'), 500
