#!/usr/bin/env python

from flask import (
    Flask, flash, get_flashed_messages,
    url_for, render_template,
    request, redirect
)
from page_analyzer.DB_queries import (
    get_DB_select_from_table,
    get_DB_insert_to_table,
    get_DB_url_page,
    get_DB_list_of_urls
)
from page_analyzer.parsing_url import parsing_url
from page_analyzer.validation_url import validation_url
from dotenv import load_dotenv
from datetime import date
import psycopg2
import os
import requests


app = Flask(__name__)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


class DataConn:

    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


@app.route('/')
def index():

    messages = get_flashed_messages(with_categories=True)

    return render_template('index.html', messages=messages)


@app.route('/urls/<id>')
def url_page(id):

    url_checks_list = []
    result_DB_query = get_DB_url_page(id)

    if type(result_DB_query) is list:
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
        url_checks_list = replace_None(url_checks_list)

    else:
        new_url, created_at = result_DB_query

    messages = get_flashed_messages(with_categories=True)

    return render_template('url_page.html', messages=messages, id=id,
                           new_url=new_url, created_at=created_at,
                           url_checks_list=url_checks_list)


@app.route('/urls/<id>/checks', methods=['POST'])
def url_checks(id):

    created_at = date.today()
    name = get_DB_select_from_table('name', 'urls', 'id', id)

    try:
        resp = requests.get(name)

    except requests.exceptions.RequestException:
        created_at = get_DB_select_from_table('created_at', 'urls', 'id', id)
        flash('Произошла ошибка при проверке', 'error')
        messages = get_flashed_messages(with_categories=True)

        return render_template('url_page.html', messages=messages, id=id,
                               new_url=name, created_at=created_at), 422

    else:
        url_status_code = resp.status_code
        if url_status_code == 200:
            url_h1, url_title, url_description = parsing_url(name)
            get_DB_insert_to_table('url_checks', 'url_id, status_code, h1,\
                                   title, description, created_at',
                                   5, id, url_status_code, url_h1, url_title,
                                   url_description, created_at)
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'error')

    return redirect(url_for('url_page', id=id), code=302)


@app.route('/urls')
def urls():

    urls = []
    list_of_urls = get_DB_list_of_urls()
    urls = sorted([{'id': item[0],
                    'name': item[1],
                    'created_at': item[2],
                    'status_code': item[3]}
                  for item in list_of_urls],
                  key=lambda k: k['id'], reverse=True)
    urls = replace_None(urls)

    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_url():
    created_at = date.today()
    new_url = request.form.get('url')

    messages = validation_url(new_url)
    if messages != []:
        return render_template('index.html', messages=messages), 422

    if get_DB_select_from_table('id', 'urls', 'name', new_url, True):
        id = get_DB_select_from_table('id', 'urls', 'name', new_url)
        flash('Страница уже существует', 'success')
        return redirect(url_for('url_page', id=id), code=302)

    get_DB_insert_to_table('urls', 'name, created_at',
                           1, new_url, created_at)
    id = get_DB_select_from_table('id', 'urls', 'name', new_url)

    flash('Страница успешно добавлена', 'success')

    return redirect(url_for('url_page', id=id), code=302)


def replace_None(list_of_dicts):
    for item in list_of_dicts:
        for key in item.keys():
            if item[key] is None:
                item[key] = ''
    return list_of_dicts
