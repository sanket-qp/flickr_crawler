import sqlite3
import settings
from crawlers import FlickrCrawler
from utils import SQLiteWriter

def setup_db(db_file):
    with sqlite3.connect(db_file) as conn:
        with open('schema.sql', 'r') as f:
            schema = f.read()
            conn.executescript(schema)

def get_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def handle_output(photo_dict):
    """
    this functions gets called when parsed metadata is available from the crawler 
    """
    if hasattr(settings, 'DB_FILE'):
        db_file = settings.DB_FILE
    else:
        db_file = 'flickr.db'

    columns = ', '.join(photo_dict.keys())
    placeholders = ', '.join('?' * len(photo_dict))
    with sqlite3.connect(db_file) as conn:
        sql = "replace into flickr_meta ({}) values ({})".format(columns, placeholders)
        cur = conn.cursor()
        cur.execute(sql, photo_dict.values())

def main():
    db_file = settings.DB_FILE if settings.DB_FILE else 'flickr.db'
    setup_db(db_file)
    
    # pass the callback function so that data can be stored in database
    start_urls = [
        'https://www.flickr.com/search/?text=paris',
        'https://www.flickr.com/search/?text=rome',
        'https://www.flickr.com/search/?text=new%20york',
    ]
    c = FlickrCrawler(start_urls, handle_output)
    c.start()

if __name__ == "__main__":
    main()
