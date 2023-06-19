#!/usr/bin/env python

from flask import (
    Flask, flash, get_flashed_messages,
    url_for, render_template,
    request, redirect
)
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import date
from bs4 import BeautifulSoup
import validators
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
        print('Database connection established')
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print('Database connection is closed')
        if exc_val:
            raise


@app.route('/')
def index():

    messages = get_flashed_messages(with_categories=True)

    return render_template('index.html', messages=messages)


@app.route('/urls/<id>')
def url_page(id):

    url_checks_list = []

    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS (SELECT url_checks.url_id\
                       FROM url_checks JOIN urls ON\
                       url_checks.url_id = urls.id\
                       WHERE urls.id = (%s))', (id,))

        if cursor.fetchone()[0]:
            cursor.execute('SELECT urls.id, urls.name, urls.created_at,\
                           url_checks.id, url_checks.status_code,\
                           url_checks.h1, url_checks.title,\
                           url_checks.description, url_checks.created_at\
                           FROM urls JOIN url_checks\
                           ON urls.id = url_checks.url_id\
                           WHERE urls.id = (%s)', (id,))
            url_checks_work_list = cursor.fetchall()
            url_checks_list = sorted([{'id': item[0], 'url_name': item[1],
                                       'created_at': item[2],
                                       'checks_id': item[3],
                                       'checks_status_code': item[4],
                                       'checks_h1': item[5],
                                       'checks_title': item[6],
                                       'checks_description': item[7],
                                       'checks_created_at': item[8]}
                                      for item in url_checks_work_list],
                                     key=lambda k: k['checks_id'],
                                     reverse=True)
            for item in url_checks_list:
                new_url = item['url_name']
                created_at = item['created_at']
                break
            url_checks_list = replace_None(url_checks_list)
            cursor.close()

        else:
            cursor.execute('SELECT name FROM urls WHERE id = (%s)', (id,))
            new_url = cursor.fetchone()[0]
            cursor.execute('SELECT created_at FROM urls\
                           WHERE id = (%s)', (id,))
            created_at = cursor.fetchone()[0]
            cursor.close()

        print([id, new_url, created_at])
        print(url_checks_list)
        messages = get_flashed_messages(with_categories=True)

    return render_template('url_page.html', messages=messages, id=id,
                           new_url=new_url, created_at=created_at,
                           url_checks_list=url_checks_list)


@app.route('/urls/<id>/checks', methods=['POST'])
def url_checks(id):

    created_at = date.today()

    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM urls WHERE id = (%s)', (id,))
        name = cursor.fetchone()[0]
        print(name)

        try:
            resp = requests.get(name)
        except requests.exceptions.RequestException:
            cursor.close()
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for('url_page', id=id), code=302)
        else:
            soup = BeautifulSoup(resp.text, 'html.parser')
            url_status_code = resp.status_code
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
            cursor.execute('INSERT INTO url_checks\
                           (url_id, status_code, h1, title, description,\
                           created_at) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id, url_status_code, url_h1, url_title,
                            url_description, created_at))
            conn.commit()
            cursor.close()
            flash('Страница успешно проверена', 'success')

    return redirect(url_for('url_page', id=id), code=302)


@app.route('/urls')
def urls():

    urls = []

    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM (SELECT urls.id, urls.name,\
                       url_checks.created_at, url_checks.status_code,\
                       url_checks.id, RANK() OVER (PARTITION BY\
                       urls.id ORDER BY url_checks.id DESC)\
                       FROM urls LEFT OUTER JOIN url_checks ON\
                       urls.id = url_checks.url_id) AS urls_rank\
                       WHERE rank = 1')
        list_of_urls = cursor.fetchall()
        cursor.close()

    print(list_of_urls)
    urls = sorted([{'id': item[0], 'name': item[1], 'created_at': item[2],
                    'status_code': item[3]} for item in list_of_urls],
                  key=lambda k: k['id'], reverse=True)
    urls = replace_None(urls)
    print(urls)

    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_url():
    created_at = date.today()
    new_url = request.form.get('url')
    work_url = urlparse(new_url)

# ------------------------------------------------------------------------
    if work_url.scheme:
        new_url = f'{work_url.scheme}://{work_url.netloc}'.lower()
    elif not work_url.scheme and len(work_url) > 255:
        flash('Некорректный URL', 'error')
        flash('URL превышает 255 символов', 'error')
        return redirect(url_for('index'), code=302)
    valid_new_url_flag = validators.url(new_url)
    if len(new_url) > 255:
        flash('URL превышает 255 символов', 'error')
        if not valid_new_url_flag:
            flash('Некорректный URL', 'error')
        return redirect(url_for('index'), code=302)
    elif not valid_new_url_flag:
        flash('Некорректный URL', 'error')
        return redirect(url_for('index'), code=302)
# ------------------------------------------------------------------------

    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS (SELECT id FROM urls WHERE name = (%s))',
                       (new_url,))

        if cursor.fetchone()[0]:
            cursor.execute('SELECT id FROM urls WHERE name = (%s)', (new_url,))
            id = cursor.fetchone()[0]
            flash('Страница уже существует', 'success')
            return redirect(url_for('url_page', id=id), code=302)

        cursor.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                       (new_url, created_at))
        conn.commit()
        cursor.execute('SELECT id FROM urls WHERE name = (%s)', (new_url,))
        id = cursor.fetchone()[0]
        cursor.close()

    flash('Страница успешно добавлена', 'success')

    return redirect(url_for('url_page', id=id), code=302)


def replace_None(list_of_dicts):
    for item in list_of_dicts:
        for key in item.keys():
            if item[key] is None:
                item[key] = ''
    return list_of_dicts


if __name__ == "__main__":
    app.run(debug=True)
