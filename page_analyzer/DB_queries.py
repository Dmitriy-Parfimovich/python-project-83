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


def get_DB_select_from_table(item, table, cond, value):
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT {item} FROM {table} WHERE {cond} = {value}',
                       (item, table, cond, value))
        result_DB_query = cursor.fetchone()[0]
        cursor.close()
        return result_DB_query


def get_DB_insert_to_table(table, item, *values):
    insert_query = f'INSERT INTO {table}({item})\
                     VALUES (%s, %s, %s, %s, %s, %s)'
    with DataConn(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()


def get_DB_url_page(id):
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
            cursor.close()
            return url_checks_work_list
        else:
            new_url = get_DB_select_from_table('name', 'urls', 'id', id)
            created_at = get_DB_select_from_table('created_at', 'urls',
                                                  'id', id)
            return (new_url, created_at)
