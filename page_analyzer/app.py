#!/usr/bin/env python

from flask import (
    Flask, flash, get_flashed_messages,
    url_for, render_template,
    request, redirect
)
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import date
import validators
import psycopg2
import os

app = Flask(__name__)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET KEY')
app.secret_key = os.getenv('SECRET_KEY')


class DataConn:

    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_name)
        print('Подключение к БД установлено')
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print('Подключение к БД закрыто')
        if exc_val:
            raise


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls/<id>')
def url_page(id):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM urls WHERE id = (%s)', (id,))
        new_url = cursor.fetchone()[0]
        cursor.execute('SELECT created_at FROM urls WHERE id = (%s)', (id,))
        created_at = cursor.fetchone()[0]
        cursor.close()
        print([id, new_url, created_at])
    messages = get_flashed_messages(with_categories=True)
    return render_template('url_page.html', messages=messages, id=id,
                           new_url=new_url, created_at=created_at)


@app.route('/urls')
def urls():
    urls = []
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM urls')
        list_of_urls = cursor.fetchall()
        cursor.close()
        print(list_of_urls)
    urls = sorted([{'id': item[0], 'name': item[1]} for item in list_of_urls],
                  key=lambda k: k['id'], reverse=True)
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


if __name__ == "__main__":
    app.run(debug=True)
