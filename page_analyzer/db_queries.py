#!/usr/bin/env python


from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class DataConn:

    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


def get_DB_select_name(id):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM urls WHERE id = (%s)', (id,))
        result_DB_query = cursor.fetchone()[0]
        cursor.close()
    return result_DB_query


def get_DB_select_id_exists(new_url):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS (SELECT id FROM urls\
                       WHERE name = (%s))', (new_url,))
        result_DB_query = cursor.fetchone()[0]
        cursor.close()
    return result_DB_query


def get_DB_select_id(new_url):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM urls WHERE name = (%s)', (new_url,))
        result_DB_query = cursor.fetchone()[0]
        cursor.close()
    return result_DB_query


def get_DB_select_created_at(id):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT created_at FROM urls WHERE id = (%s)', (id,))
        result_DB_query = cursor.fetchone()[0]
        cursor.close()
    return result_DB_query


def get_DB_insert_url_checks(*values):
    insert_query = 'INSERT INTO url_checks(url_id,\
                    status_code, h1, title, description,\
                    created_at) VALUES (%s, %s, %s, %s, %s, %s)'
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()


def get_DB_insert_add_url(*values):
    insert_query = 'INSERT INTO urls(name, created_at)\
                    VALUES (%s, %s)'
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()


def get_DB_url_page(id):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT urls.id, urls.name, urls.created_at,\
                           url_checks.id, url_checks.status_code,\
                           url_checks.h1, url_checks.title,\
                           url_checks.description, url_checks.created_at\
                           FROM urls JOIN url_checks\
                           ON urls.id = url_checks.url_id\
                           WHERE urls.id = (%s)', (id,))
        url_checks_work_list = cursor.fetchall()
        if url_checks_work_list == []:
            cursor.execute('SELECT name, created_at FROM urls\
                           WHERE id = (%s)', (id,))
            name_created_at = cursor.fetchone()
            cursor.close()
            return name_created_at
        cursor.close()
        return url_checks_work_list


def get_DB_list_of_urls():
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
    return list_of_urls
