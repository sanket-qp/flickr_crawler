# flickr_crawler
Simple Flickr Crawler

This is a simple library for crawling **search results pages** of flickr.com. it uses python's multiprocessing module to crawl the webpages and collects the metadata about photos in parallel. 

## Quick Start 
```python
from crawlers import FlickrCrawler
flickr = FlickrCrawler(['https://www.flickr.com/search/?text=paris'])
flickr.start()
```
You can also provide callback functions when parsed data is available
```python
from crawlers import FlickrCrawler

def save_to_db(metadata_dict):
    """
    saves the data to database 
    """
    pass

flickr = FlickrCrawler(['https://www.flickr.com/search/?text=paris'], save_to_db)
flickr.start()
```

## Installation
```python
pip install -r requirement.txt
```

## Settings
please modifiy crawlers/settings.py according to your needs.

## Demo Application 
I've provided a demo application showing the usage of library. it provides a callback which saves the data in to sqlite database.
you can change the database settings in settings.py
database schema is stored in 
```sql
schema.sql
```
app.py takes care of setting up the database, you can run the application by running following command

```python
python app.py
```
